import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from scipy.signal import periodogram
import pymannkendall as mk
import statsmodels.api as sm

class ProductSalesAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
        self.df.rename(columns={self.df.columns[0]: 'DATE'}, inplace=True)
        self.df['DATE'] = pd.to_datetime(self.df['DATE'], format='%Y%m')
        self.df.set_index('DATE', inplace=True)

    def detect_periodicity(self, time_series):
        acf_values = sm.tsa.acf(time_series, nlags=len(time_series) // 2)
        max_acf_idx = np.argmax(np.abs(acf_values[2:])) + 2
        max_acf = acf_values[max_acf_idx]
        return max_acf, max_acf_idx

    def adf_test(self, time_series):
        adf_result = adfuller(time_series)
        return adf_result[1]

    def classical_decomposition(self, time_series):
        decomposition = seasonal_decompose(time_series, model='additive', period=12)
        trend = decomposition.trend
        seasonal = decomposition.seasonal
        resid = decomposition.resid
        Var_Rt = resid.var()
        Var_Tt_plus_Rt = (trend + resid).var()
        Var_St_plus_Rt = (seasonal + resid).var()
        F_T = max(0, 1 - Var_Rt / Var_Tt_plus_Rt)
        F_S = max(0, 1 - Var_Rt / Var_St_plus_Rt)
        Residual_Std_Ratio = resid.std() / time_series.std()
        return F_T, F_S, Residual_Std_Ratio

    def periodogram_analysis(self, time_series):
        freqs, power = periodogram(time_series)
        periods = 1 / freqs
        main_period_index = np.argmax(power[1:]) + 1
        main_period = periods[main_period_index]
        if main_period == len(time_series):
            return None, None
        else:
            main_power = power[main_period_index]
            return main_period, main_power

    def mann_kendall_trend(self, time_series):
        test_result = mk.yue_wang_modification_test(time_series)
        return test_result.trend, test_result.p

    def lyapunov_exponent(self, series, freq):
        N = len(series)
        if freq > N - 10:
            raise ValueError("Insufficient data")
        Ly = np.zeros(N - freq)
        for i in range(N - freq):
            differences = np.abs(series[i] - series)
            sorted_indices = np.argsort(differences)
            valid_indices = sorted_indices[sorted_indices < (N - freq)]
            if len(valid_indices) < 2:
                continue
            j = valid_indices[1]
            Ly[i] = np.log(np.abs((series[i + freq] - series[j + freq]) / (series[i] - series[j]))) / freq
            if np.isnan(Ly[i]) or np.isinf(Ly[i]):
                Ly[i] = np.nan
        Lyap = np.nanmean(Ly)
        fLyap = np.exp(Lyap) / (1 + np.exp(Lyap))
        return fLyap

    def stl_decomposition(self, time_series):
        stl = STL(time_series, seasonal=13, trend=25, robust=True)
        res = stl.fit()

        R_t = res.resid
        T_t = res.trend
        S_t = res.seasonal

        Var_Rt = R_t.var()
        Var_Tt_plus_Rt = (T_t + R_t).var()
        Var_St_plus_Rt = (S_t + R_t).var()

        F_T = max(0, 1 - Var_Rt / Var_Tt_plus_Rt)
        F_S = max(0, 1 - Var_Rt / Var_St_plus_Rt)

        Residual_Std_Ratio = R_t.std() / time_series.std()
        return S_t, F_T, F_S, Residual_Std_Ratio

    def analyze_products(self):
        results = []

        for product in self.df.columns:
            time_series = self.df[product].dropna()
            if time_series.nunique() <= 1:
                print(f"Product {product} has insufficient data variation for analysis.")
                continue
            S_t, stl_F_T, stl_F_S, stl_Residual_Std_Ratio = self.stl_decomposition(time_series)
            max_acf,max_acf_idx = self.detect_periodicity(S_t)
            adf_p_value = self.adf_test(time_series)
            F_T, F_S, Residual_Std_Ratio = self.classical_decomposition(time_series)
            main_period, main_power = self.periodogram_analysis(time_series)
            trend, p_value = self.mann_kendall_trend(time_series)
            try:
                fLyap = self.lyapunov_exponent(time_series.values, freq=10)
            except ValueError:
                fLyap = np.nan


            results.append({
                'Product_code': product,
                'ACF_VALUE': max_acf,
                'period': max_acf_idx,
                'ADF_P_value': adf_p_value,
                'Classical_Trend_Strength': F_T,
                'Classical_Seasonal_Strength': F_S,
                'Classical_Residual_Std_Ratio': Residual_Std_Ratio,
                'STL_Trend_Strength': stl_F_T,
                'STL_Seasonal_Strength': stl_F_S,
                'STL_Residual_Std_Ratio': stl_Residual_Std_Ratio,
                'Main_Period': main_period,
                'Long_Term_Trend': trend,
                'Long_Term_P_value': p_value,
                'Lyapunov_Exponent': fLyap
            })

        return results

    def save_results(self, results, output_file):
        results_df = pd.DataFrame(results)
        results_df.to_excel(output_file, index=False)
        print(f"All results have been saved to {output_file}")

# 使用示例
file_path = 'C:\\python_study\\supply_chain_huawei\\Classification\\data\\product_sales_data.xlsx'  # 请将路径替换为你的 Excel 文件路径
analysis = ProductSalesAnalysis(file_path)
results = analysis.analyze_products()
output_file = 'combined_results.xlsx'
analysis.save_results(results, output_file)

import sys
import math
import numpy as np
import pandas as pd

def __get_RS(series):
    incs = series
    mean_inc = np.sum(incs) / len(incs)
    deviations = incs - mean_inc
    Z = np.cumsum(deviations)
    R = max(Z) - min(Z)
    S = np.std(incs, ddof=1)

    if R == 0 or S == 0:
        return 0  # return 0 to skip this interval due undefined R/S

    return R / S

def compute_Hc(series, min_window=10, max_window=None, simplified=True, min_sample=30):
    if len(series) < min_sample:
        raise ValueError(f"Series length must be greater or equal to min_sample={min_sample}")

    ndarray_likes = [np.ndarray]
    if "pandas.core.series" in sys.modules.keys():
        ndarray_likes.append(pd.core.series.Series)

    # convert series to numpy array if series is not numpy array or pandas Series
    if type(series) not in ndarray_likes:
        series = np.array(series)

    if "pandas.core.series" in sys.modules.keys() and type(series) == pd.core.series.Series:
        if series.isnull().values.any():
            raise ValueError("Series contains NaNs")
        series = series.values  # convert pandas Series to numpy array
    elif np.isnan(np.min(series)):
        raise ValueError("Series contains NaNs")

    RS_func = __get_RS

    err = np.geterr()
    np.seterr(all='raise')

    max_window = max_window or len(series) - 1
    window_sizes = list(map(
        lambda x: int(10**x),
        np.arange(math.log10(min_window), math.log10(max_window), 0.25)))
    window_sizes.append(len(series))

    RS = []
    for w in window_sizes:
        rs = []
        for start in range(0, len(series), w):
            if (start + w) > len(series):
                break
            _ = RS_func(series[start:start + w])
            if _ != 0:
                rs.append(_)
        RS.append(np.mean(rs))

    A = np.vstack([np.log10(window_sizes), np.ones(len(RS))]).T
    H, c = np.linalg.lstsq(A, np.log10(RS), rcond=-1)[0]
    np.seterr(**err)

    c = 10**c
    return H, c, [window_sizes, RS]

if __name__ == '__main__':
    # 读取 Excel 文件
    file_path = 'C:\\python_study\\supply_chain_huawei\\Classification\\data\\product_sales_data.xlsx'  # 请将路径替换为你的 Excel 文件路径
    df = pd.read_excel(file_path)

    # 确保第一列为日期列，其他列为产品编码
    df.rename(columns={df.columns[0]: 'DATE'}, inplace=True)
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m')
    df.set_index('DATE', inplace=True)

    # 初始化结果列表
    results = []

    # 对每个产品单独计算赫斯特指数
    for product in df.columns:
        time_series = df[product].dropna().values

        if len(time_series) < 30:
            print(f"Product {product} has insufficient data for Hurst exponent calculation.")
            continue

        # 计算赫斯特指数
        H, c, data = compute_Hc(time_series, simplified=True)

        results.append({
            'Product_code': product,
            'Hurst_exponent': H,
            'c': c
        })

    # 将结果转换为 DataFrame 并保存到 Excel 文件
    results_df = pd.DataFrame(results)
    output_file_path = 'hurst_exponent_results.xlsx'
    results_df.to_excel(output_file_path, index=False)

    print(f"赫斯特指数计算结果已保存到 {output_file_path}")

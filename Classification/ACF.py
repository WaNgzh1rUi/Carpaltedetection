import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
from scipy import signal
# 读取 Excel 文件
file_path = 'C:\\python_study\\supply_chain_huawei\\Classification\\data\\product_sales_data.xlsx'  # 请将路径替换为你的 Excel 文件路径
df = pd.read_excel(file_path)

# 确保第一列为日期列，其他列为产品编码
df.rename(columns={df.columns[0]: 'DATE'}, inplace=True)
df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m')
df.set_index('DATE', inplace=True)


# 周期性检测
def detect_periodicity(time_series):
    acf_values = sm.tsa.acf(time_series, nlags=len(time_series) // 2)
    max_acf = np.max(np.abs(acf_values[2:]))  # 从lag 2开始计算最大绝对值
    return max_acf


# 初始化结果列表
results = []
# 对每个产品单独计算最大ACF值
for product in df.columns:
    time_series = df[product].dropna()

    if time_series.nunique() <= 1:
        print(f"Product {product} has insufficient data variation for trend detection.")
        continue
    time_series = signal.detrend(time_series)
    # 计算最大ACF值
    max_acf = detect_periodicity(time_series)
    plot_acf(time_series,adjusted=True)
    # plot_pacf(time_series)
    results.append({
        'Product_code': product,
        'MAX_ACF_VALUE': max_acf
    })

# 将结果转换为 DataFrame 并保存到 Excel 文件
results_df = pd.DataFrame(results)
output_file_path = 'acf_values_results.xlsx'
results_df.to_excel(output_file_path, index=False)
print(f"最大ACF值已保存到 {output_file_path}")
plt.show()
plt.plot(results_df['MAX_ACF_VALUE'])
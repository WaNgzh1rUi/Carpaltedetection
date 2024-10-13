import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller

# 读取 Excel 文件
file_path = 'C:\\python_study\\supply_chain_huawei\\Classification\\data\\product_sales_data.xlsx'  # 请将路径替换为你的 Excel 文件路径
df = pd.read_excel(file_path)

# 确保第一列为日期列，其他列为产品编码
df.rename(columns={df.columns[0]: 'DATE'}, inplace=True)
df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m')
df.set_index('DATE', inplace=True)

# 初始化结果列表
results = []

# 对每个产品进行 ADF 平稳性检验
for product_code in df.columns:
    # 提取特定产品的时间序列数据
    ts = df[product_code].dropna()

    # 进行 ADF 平稳性检验
    adf_result = adfuller(ts)
    adf_statistic = adf_result[0]
    p_value = adf_result[1]
    critical_values = adf_result[4]

    # 根据 p 值判断稳定性
    stability = '稳定型序列' if p_value < 0.05 else '非稳定型序列'

    # 将结果添加到列表中
    results.append([product_code, p_value])
    #
    # # 创建图形
    # plt.figure(figsize=(10, 5))
    # plt.plot(ts)
    # plt.title(f'Product {product_code} - Time Series')
    # plt.xlabel('Date')
    # plt.ylabel('Value')
    # plt.grid(True)
    # plt.show()

# 创建 DataFrame 并保存到 Excel
results_df = pd.DataFrame(results, columns=['Product Code',  'p-value'])

print(results_df)
output_file_path = 'adf_test_results.xlsx'  # 请将路径替换为你想保存的 Excel 文件路径
results_df.to_excel(output_file_path, index=False)
print(f"ADF test results have been saved to {output_file_path}")

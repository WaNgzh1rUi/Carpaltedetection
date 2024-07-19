import pandas as pd
import pickle

demand_file_path = 'C:/python_study/supply_chain_huawei/data/测试数据_生成.xlsx'  # 替换为你的文件路径

# 读取数据
demand_data = pd.read_excel(demand_file_path,
                            dtype={'represent_office': str, 'dealer': str, 'product_family': str, 'product_model': str,
                                   'demand': int, 'date': str})

demand_data.columns = ['represent_office', 'dealer', 'product_family', 'product_model', 'demand', 'date']

represent_id_maps = []
dealer_id_maps = []
product_family_id_maps = []
product_model_id_maps = []

# 全局ID计数器
unique_id = 0

# 节点信息存储
node_demand_data = {}


# 基于不同层级分配ID
def assign_ids(demand_data, levels):
    global unique_id
    unique_id = 0
    represent_id_maps.clear()
    dealer_id_maps.clear()
    product_family_id_maps.clear()
    product_model_id_maps.clear()
    node_demand_data.clear()

    if 'region' in levels:
        pass
    # 代表处ID分配
    if 'represent_office' in levels:
        rep_uni_data = demand_data['represent_office'].drop_duplicates()
        for rep_name in rep_uni_data:
            unique_id += 1
            represent_id_maps.append((unique_id, rep_name))

    # 经销商ID分配
    if 'dealer' in levels:
        if 'represent_office' in levels:
            for rep_name in [x[1] for x in represent_id_maps]:
                dealer_uni_data = demand_data[demand_data['represent_office'] == rep_name]['dealer'].drop_duplicates()
                for dealer_name in dealer_uni_data:
                    unique_id += 1
                    dealer_id_maps.append((unique_id, dealer_name, rep_name))  # 保存rep_name用于参考
        else:
            dealer_uni_data = demand_data['dealer'].drop_duplicates()
            for dealer_name in dealer_uni_data:
                unique_id += 1
                dealer_id_maps.append((unique_id, dealer_name, None))

    # 产品族ID分配
    if 'product_family' in levels:
        if 'dealer' in levels:
            for _, dealer_name, rep_name in [x for x in dealer_id_maps]:
                family_uni_data = demand_data[(rep_name is None or (demand_data['represent_office'] == rep_name)) & (
                        demand_data['dealer'] == dealer_name)]['product_family'].drop_duplicates()
                for family_name in family_uni_data:
                    unique_id += 1
                    product_family_id_maps.append((unique_id, family_name, dealer_name, rep_name))
        else:
            family_uni_data = demand_data['product_family'].drop_duplicates()
            for family_name in family_uni_data:
                unique_id += 1
                product_family_id_maps.append((unique_id, family_name, None, None))

    # ITEM ID分配
    if 'product_model' in levels:
        if 'product_family' in levels:
            for family_id, family_name, dealer_name, rep_name in [x for x in product_family_id_maps]:
                model_uni_data = demand_data[
                    (demand_data['product_family'] == family_name) & (
                            dealer_name is None or (demand_data['dealer'] == dealer_name)) & (
                            rep_name is None or (demand_data['represent_office'] == rep_name))][
                    'product_model'].drop_duplicates()
                for model_name in model_uni_data:
                    unique_id += 1
                    product_model_id_maps.append((unique_id, model_name, family_name, dealer_name, rep_name))
        elif 'dealer' in levels:
            for dealer_id, dealer_name, rep_name in [x for x in dealer_id_maps]:
                model_uni_data = demand_data[
                    (demand_data['dealer'] == dealer_name) & (
                            rep_name is None or (demand_data['represent_office'] == rep_name))][
                    'product_model'].drop_duplicates()
                for model_name in model_uni_data:
                    unique_id += 1
                    product_model_id_maps.append((unique_id, model_name, None, dealer_name, rep_name))
        else:
            model_uni_data = demand_data['product_model'].drop_duplicates()
            for model_name in model_uni_data:
                unique_id += 1
                product_model_id_maps.append((unique_id, model_name, None, None, None))


# 需求计算函数
def calculate_demand_data(demand_data, levels):
    result_data = []
    assign_ids(demand_data, levels)

    # 获取所有日期
    date_list = demand_data['date'].unique().tolist()
    date_list.sort()

    # 计算节点总需求
    def calculate_total_demand(subset_data, date_list, id_value, level_info):
        for date_str in date_list:
            total_demand = subset_data[subset_data['date'] == date_str]['demand'].sum()
            result_data.append([id_value, date_str, total_demand])
            node_key = (*level_info, date_str)
            node_demand_data[node_key] = total_demand

    if 'region' in levels:
        pass
    # 对不同层级进行需求计算
    if 'represent_office' in levels:
        for rep_id, rep_name in represent_id_maps:
            rep_data = demand_data[demand_data['represent_office'] == rep_name]
            calculate_total_demand(rep_data, date_list, rep_id, (rep_name,))

            if 'dealer' in levels:
                for dealer_id, dealer_name, _ in [x for x in dealer_id_maps if x[2] == rep_name]:
                    dealer_data = rep_data[rep_data['dealer'] == dealer_name]
                    calculate_total_demand(dealer_data, date_list, dealer_id, (rep_name, dealer_name))

                    if 'product_family' in levels:
                        for family_id, family_name, _, _ in [x for x in product_family_id_maps if
                                                             x[2] == dealer_name and x[3] == rep_name]:
                            family_data = dealer_data[dealer_data['product_family'] == family_name]
                            calculate_total_demand(family_data, date_list, family_id,
                                                   (rep_name, dealer_name, family_name))

                            if 'product_model' in levels:
                                for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if
                                                                      x[2] == family_name and x[3] == dealer_name and x[
                                                                          4] == rep_name]:
                                    model_data = family_data[family_data['product_model'] == model_name]
                                    calculate_total_demand(model_data, date_list, model_id,
                                                           (rep_name, dealer_name, family_name, model_name))
                    elif 'product_model' in levels:
                        for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if
                                                              x[3] == dealer_name and x[4] == rep_name]:
                            model_data = dealer_data[dealer_data['product_model'] == model_name]
                            calculate_total_demand(model_data, date_list, model_id, (rep_name, dealer_name, model_name))
            elif 'product_family' in levels:
                for family_id, family_name, _, _ in [x for x in product_family_id_maps if x[3] == rep_name]:
                    family_data = rep_data[rep_data['product_family'] == family_name]
                    calculate_total_demand(family_data, date_list, family_id, (rep_name, family_name))

                    if 'product_model' in levels:
                        for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if
                                                              x[2] == family_name and x[4] == rep_name]:
                            model_data = family_data[family_data['product_model'] == model_name]
                            calculate_total_demand(model_data, date_list, model_id, (rep_name, family_name, model_name))
            elif 'product_model' in levels:
                for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if x[4] == rep_name]:
                    model_data = rep_data[rep_data['product_model'] == model_name]
                    calculate_total_demand(model_data, date_list, model_id, (rep_name, model_name))
    elif 'dealer' in levels:
        for dealer_id, dealer_name, rep_name in dealer_id_maps:
            dealer_data = demand_data[demand_data['dealer'] == dealer_name]
            calculate_total_demand(dealer_data, date_list, dealer_id, (rep_name, dealer_name))

            if 'product_family' in levels:
                for family_id, family_name, _, _ in [x for x in product_family_id_maps if x[2] == dealer_name]:
                    family_data = dealer_data[dealer_data['product_family'] == family_name]
                    calculate_total_demand(family_data, date_list, family_id, (rep_name, dealer_name, family_name))

                    if 'product_model' in levels:
                        for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if
                                                              x[2] == family_name and x[3] == dealer_name]:
                            model_data = family_data[family_data['product_model'] == model_name]
                            calculate_total_demand(model_data, date_list, model_id,
                                                   (rep_name, dealer_name, family_name, model_name))
            elif 'product_model' in levels:
                for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if x[3] == dealer_name]:
                    model_data = dealer_data[dealer_data['product_model'] == model_name]
                    calculate_total_demand(model_data, date_list, model_id, (rep_name, dealer_name, model_name))
    elif 'product_family' in levels:
        for family_id, family_name, dealer_name, rep_name in product_family_id_maps:
            family_data = demand_data[demand_data['product_family'] == family_name]
            calculate_total_demand(family_data, date_list, family_id, (rep_name, dealer_name, family_name))

            if 'product_model' in levels:
                for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if x[2] == family_name]:
                    model_data = family_data[family_data['product_model'] == model_name]
                    calculate_total_demand(model_data, date_list, model_id,
                                           (rep_name, dealer_name, family_name, model_name))
    elif 'product_model' in levels:
        for model_id, model_name, _, _, _ in product_model_id_maps:
            model_data = demand_data[demand_data['product_model'] == model_name]
            calculate_total_demand(model_data, date_list, model_id, (model_name,))

    # 计算地区部的总需求
    for date_str in date_list:
        total_demand = demand_data[demand_data['date'] == date_str]['demand'].sum()
        result_data.append([0, date_str, total_demand])

    output_df = pd.DataFrame(result_data, columns=['id', 'date', 'total_demand'])

    # 数据透视表
    unique_dates = output_df['date'].unique()
    unique_ids = output_df['id'].unique()
    pivot_df = output_df.pivot(index='date', columns='id', values='total_demand')
    pivot_df = pivot_df.reindex(index=unique_dates, columns=unique_ids)

    id_names = ['总需求']
    id_names.extend([x[1] for x in represent_id_maps])
    id_names.extend([x[1] for x in dealer_id_maps])
    id_names.extend([x[1] for x in product_family_id_maps])
    id_names.extend([x[1] for x in product_model_id_maps])
    id_names_row = pd.DataFrame([id_names], index=['中文名称'])
    pivot_df = pd.concat([pivot_df, id_names_row], axis=0)
    return pivot_df


def query_demand_data(node_info):
    if node_info not in node_demand_data:
        return None
    else:
        return node_demand_data[node_info]


def query_total_demand(node_info):
    # 根据节点信息找到对应的id
    target_id = None
    if len(node_info) == 1:
        for rep_id, rep_name in represent_id_maps:
            if rep_name == node_info[0]:
                target_id = rep_id
                break
    elif len(node_info) == 2:
        for dealer_id, dealer_name, rep_name in dealer_id_maps:
            if rep_name == node_info[0] and dealer_name == node_info[1]:
                target_id = dealer_id
                break
    elif len(node_info) == 3:
        for family_id, family_name, dealer_name, rep_name in product_family_id_maps:
            if rep_name == node_info[0] and dealer_name == node_info[1] and family_name == node_info[2]:
                target_id = family_id
                break
    elif len(node_info) == 4:
        for model_id, model_name, family_name, dealer_name, rep_name in product_model_id_maps:
            if rep_name == node_info[0] and dealer_name == node_info[1] and family_name == node_info[
                2] and model_name == node_info[3]:
                target_id = model_id
                break

    if target_id is None:
        return None

    # 从result_df中找到对应的列
    total_demand_data = result_df[target_id]

    return total_demand_data


# 提示用户输入层级
def prompt_user_input():
    print("请输入需要分析的层级（以逗号分隔）：")
    print("可选层级：region,represent_office, dealer, product_family, product_model")
    user_input = input("输入层级: ").strip().split(',')

    levels = [level.strip() for level in user_input]

    # 检查输入的层级是否有效
    valid_levels = {'region', 'represent_office', 'dealer', 'product_family', 'product_model'}
    if not set(levels).issubset(valid_levels):
        print("输入的层级无效，请重新输入。")
        return prompt_user_input()

    return levels


# 使用实例
levels = prompt_user_input()
result_df = calculate_demand_data(demand_data, levels)

# 节点需求数据输出为pkl文件（格式 ('西藏代表处', '经销商22', 202209, 销量: 92）)
node_demand_file_path = 'C:/python_study/supply_chain_huawei/data/node_demand_data.pkl'
with open(node_demand_file_path, 'wb') as f:
    pickle.dump(node_demand_data, f)
print("Node demand data saved to", node_demand_file_path)

# 输出节点映射字典文件，用于查询（输出表格中的每一个序号对应的结构信息，如（2，'西藏代表处', '经销商22'））
node_map = {'represent_map': represent_id_maps, 'dealer_map': dealer_id_maps, 'family_map': product_family_id_maps,
            'model_map': product_model_id_maps}
print(node_map)
node_map_file_path = 'C:/python_study/supply_chain_huawei/data/node_map_data.pkl'
with open(node_map_file_path, 'wb') as f:
    pickle.dump(node_map, f)
print("Node demand data saved to", node_map_file_path)

# 输出模型所需要的格式数据
output_file_path = 'C:/python_study/supply_chain_huawei/data/result.xlsx'
result_df.to_excel(output_file_path, index=True, header=True)
print("Output saved to", output_file_path)

# 节点信息查询示例（月度销量）
node_info = ('西藏代表处', '经销商22', 202209)
node_demand = query_demand_data(node_info)
if node_demand is not None:
    print(f"该节点的信息是 {node_info}，销量是: {node_demand}")
else:
    print(f"没有找到该节点信息，请确认输入是否正确")

# 节点信息查询示例（序列）
node_info_summary = ['西藏代表处', '经销商22']
node_demand_summary = query_total_demand(node_info_summary)
if node_demand_summary is not None:
    print(f"该节点的信息是 {node_info_summary}，销量总和如下: \n{node_demand_summary}")
else:
    print(f"没有找到该节点信息，请确认输入是否正确")

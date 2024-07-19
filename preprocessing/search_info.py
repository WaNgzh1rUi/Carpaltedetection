import pandas as pd

node_demand_data = pd.read_pickle('C:\\python_study\\supply_chain_huawei\\data\\node_demand_data.pkl')
node_map_data = pd.read_pickle('C:\\python_study\\supply_chain_huawei\\data\\node_map_data.pkl')
result_df = pd.read_excel('C:\\python_study\\supply_chain_huawei\\data\\result.xlsx', index_col=0)
print(node_demand_data)
print(node_map_data)


def query_demand_data(node_info):
    if node_info not in node_demand_data:
        return None
    else:
        return node_demand_data[node_info]


def query_total_demand(node_info):
    # 根据节点信息找到对应的id
    target_id = None
    if len(node_info) == 1:
        for rep_id, rep_name in node_map_data['represent_map']:
            if rep_name == node_info[0]:
                target_id = rep_id
                break
    elif len(node_info) == 2:
        for dealer_id, dealer_name, rep_name in node_map_data['dealer_map']:
            if rep_name == node_info[0] and dealer_name == node_info[1]:
                target_id = dealer_id
                break
    elif len(node_info) == 3:
        for family_id, family_name, dealer_name, rep_name in node_map_data['family_map']:
            if rep_name == node_info[0] and dealer_name == node_info[1] and family_name == node_info[2]:
                target_id = family_id
                break
    elif len(node_info) == 4:
        for model_id, model_name, family_name, dealer_name, rep_name in node_map_data['model_map']:
            if rep_name == node_info[0] and dealer_name == node_info[1] and family_name == node_info[
                2] and model_name == node_info[3]:
                target_id = model_id
                break

    if target_id is None:
        return None

    # 从result_df中找到对应的列
    total_demand_data = result_df[target_id]

    return total_demand_data


# 节点信息查询示例（月度销量）
node_info = ('西藏代表处', '经销商22', 202209)
node_demand = query_demand_data(node_info)
if node_demand is not None:
    print(f"该节点的信息是 {node_info}，销量是: {node_demand}")
else:
    print(f"没有找到该节点信息，请确认输入是否正确")

# 节点信息查询示例（序列）
node_info_summary = ['西藏代表处']
node_demand_summary = query_total_demand(node_info_summary)
if node_demand_summary is not None:
    print(f"该节点的信息是 {node_info_summary}，各月销量如下: \n{node_demand_summary}")
else:
    print(f"没有找到该节点信息，请确认输入是否正确")

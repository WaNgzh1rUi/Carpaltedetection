import pandas as pd

node_map_data = pd.read_pickle('C:\\python_study\\supply_chain_huawei\\data\\node_map_data.pkl')

rep_map = node_map_data['represent_map']
dealer_map = node_map_data['dealer_map']
family_map = node_map_data['family_map']
model_map = node_map_data['model_map']  # 如果没有这一层，则为空

layer_num = int(input("请输入层数："))
structure_list = []  # 存储最终的结构列表

# 获取第一层的node
curr_list = []
curr_list.append(len(rep_map))
structure_list.append(curr_list)

# 获取第二层的node
if layer_num >= 2:
    curr_list = []
    second_layer = []
    for _, x1 in [x for x in rep_map]:
        for _, x2, x1 in [x for x in dealer_map if x[2] == x1]:
            second_layer.append((x1, x2))
        curr_list.append(len(second_layer))
        second_layer.clear()
    structure_list.append(curr_list)

# 获取第三层的node
if layer_num >= 3:
    curr_list = []
    third_layer = []
    for _, x1 in [x for x in rep_map]:
        for _, x2, x1 in [x for x in dealer_map if x[2] == x1]:
            for _, x3, x2, x1 in [x for x in family_map if x[2] == x2 and x[3] == x1]:
                third_layer.append((x1, x2, x3))
            curr_list.append(len(third_layer))
            third_layer.clear()
    structure_list.append(curr_list)

# 获取第四层的node
if layer_num >= 4:
    curr_list = []
    fourth_layer = []
    for _, x1 in [x for x in rep_map]:
        for _, x2, x1 in [x for x in dealer_map if x[2] == x1]:
            for _, x3, x2, x1 in [x for x in family_map if x[2] == x2 and x[3] == x1]:
                for _, x4, x3, x2, x1 in [x for x in model_map if x[2] == x3 and x[3] == x2 and x[4] == x1]:
                    fourth_layer.append((x1, x2, x3, x4))
                curr_list.append(len(fourth_layer))
                fourth_layer.clear()
    structure_list.append(curr_list)
print(structure_list)

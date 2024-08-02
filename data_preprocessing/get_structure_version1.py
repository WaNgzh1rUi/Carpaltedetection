import pandas as pd

node_map_data = pd.read_pickle('C:\\python_study\\supply_chain_huawei\\data\\node_map_data.pkl')

node_map_data = {k: v for k, v in node_map_data.items() if v}
key_list = []
for key in node_map_data.keys():
    key_list.append(key)
    node_map_data[key] = [tuple(x for x in item if x is not None) for item in node_map_data[key]]
print(node_map_data)
print(key_list)
layer_num = int(input("请输入层数："))
if layer_num >= 2:
    second_map_data = node_map_data[key_list[0]]
if layer_num >= 3:
    third_map_data = node_map_data[key_list[1]]
if layer_num >= 4:
    fourth_map_data = node_map_data[key_list[2]]
if layer_num >= 5:
    fifth_map_data = node_map_data[key_list[3]]

structure_list = []  # 存储最终的结构列表

# 获取第一层的node
curr_list = []
curr_list.append(len(second_map_data))
structure_list.append(curr_list)

# 获取第二层的node
if layer_num >= 3:
    curr_list = []
    second_layer = []
    for _, x1 in [x for x in second_map_data]:
        for _, x2, x1 in [x for x in third_map_data if x[2] == x1]:
            second_layer.append((x1, x2))
        curr_list.append(len(second_layer))
        second_layer.clear()
    structure_list.append(curr_list)

# 获取第三层的node
if layer_num >= 4:
    curr_list = []
    third_layer = []
    for _, x1 in [x for x in second_map_data]:
        for _, x2, x1 in [x for x in third_map_data if x[2] == x1]:
            for _, x3, x2, x1 in [x for x in fourth_map_data if x[2] == x2 and x[3] == x1]:
                third_layer.append((x1, x2, x3))
            curr_list.append(len(third_layer))
            third_layer.clear()
    structure_list.append(curr_list)

# 获取第四层的node
if layer_num >= 5:
    curr_list = []
    fourth_layer = []
    for _, x1 in [x for x in second_map_data]:
        for _, x2, x1 in [x for x in third_map_data if x[2] == x1]:
            for _, x3, x2, x1 in [x for x in fourth_map_data if x[2] == x2 and x[3] == x1]:
                for _, x4, x3, x2, x1 in [x for x in fifth_map_data if x[2] == x3 and x[3] == x2 and x[4] == x1]:
                    fourth_layer.append((x1, x2, x3, x4))
                curr_list.append(len(fourth_layer))
                fourth_layer.clear()
    structure_list.append(curr_list)
print(structure_list)

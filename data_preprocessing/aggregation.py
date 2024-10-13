import pandas as pd

# Load the Excel file
demand_file_path = 'C:/python_study/supply_chain_huawei/data/测试数据_生成.xlsx'  # Replace with your file path

# Reading the excel file
demand_data = pd.read_excel(demand_file_path)

# Rename columns
demand_data.columns = ['represent_office', 'dealer', 'product_family', 'product_model', 'demand', 'date']

# Mapping dictionaries
represent_id_maps = []
dealer_id_maps = []
product_family_id_maps = []
product_model_id_maps = []

# Global ID counter
unique_id = 0


# Function to assign IDs dynamically based on active levels
def assign_ids(demand_data, levels):
    global unique_id
    unique_id = 0
    represent_id_maps.clear()
    dealer_id_maps.clear()
    product_family_id_maps.clear()
    product_model_id_maps.clear()

    if 'region' in levels:
        pass
    # Assign represent_office id
    if 'represent_office' in levels:
        rep_uni_data = demand_data['represent_office'].drop_duplicates()
        for rep_name in rep_uni_data:
            unique_id += 1
            represent_id_maps.append((unique_id, rep_name))

    # Assign dealer id
    if 'dealer' in levels:
        if 'represent_office' in levels:
            for rep_name in [x[1] for x in represent_id_maps]:
                dealer_uni_data = demand_data[demand_data['represent_office'] == rep_name]['dealer'].drop_duplicates()
                for dealer_name in dealer_uni_data:
                    unique_id += 1
                    dealer_id_maps.append((unique_id, dealer_name, rep_name))  # Save rep_name for reference
        else:
            dealer_uni_data = demand_data['dealer'].drop_duplicates()
            for dealer_name in dealer_uni_data:
                unique_id += 1
                dealer_id_maps.append((unique_id, dealer_name, None))

    # Assign product_family id
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

    # Assign product_model id
    if 'product_model' in levels:
        if 'product_family' in levels:
            for family_id, family_name, dealer_name, rep_name in [x for x in product_family_id_maps]:
                model_uni_data = demand_data[
                    (demand_data['product_family'] == family_name) & (dealer_name is None or (demand_data['dealer'] == dealer_name)) & (
                                rep_name is None or (demand_data['represent_office'] == rep_name))]['product_model'].drop_duplicates()
                for model_name in model_uni_data:
                    unique_id += 1
                    product_model_id_maps.append((unique_id, model_name, family_name, dealer_name, rep_name))
        elif 'dealer' in levels:
            for dealer_id, dealer_name, rep_name in [x for x in dealer_id_maps]:
                model_uni_data = demand_data[
                    (demand_data['dealer'] == dealer_name) & (rep_name is None or (demand_data['represent_office'] == rep_name))]['product_model'].drop_duplicates()
                for model_name in model_uni_data:
                    unique_id += 1
                    product_model_id_maps.append((unique_id, model_name, None, dealer_name, rep_name))
        else:
            model_uni_data = demand_data['product_model'].drop_duplicates()
            for model_name in model_uni_data:
                unique_id += 1
                product_model_id_maps.append((unique_id, model_name, None, None, None))


# Function to calculate and output demand data
def calculate_demand_data(demand_data, levels):
    result_data = []
    assign_ids(demand_data, levels)

    # Get all dates
    date_list = demand_data['date'].unique().tolist()
    date_list.sort()

    # Function to calculate total demand for a given data subset
    def calculate_total_demand(subset_data, date_list, id_value):
        for date_str in date_list:
            total_demand = subset_data[subset_data['date'] == date_str]['demand'].sum()
            result_data.append([id_value, date_str, total_demand])

    if 'region' in levels:
        pass
    # Calculate demand based on levels
    if 'represent_office' in levels:
        for rep_id, rep_name in represent_id_maps:
            rep_data = demand_data[demand_data['represent_office'] == rep_name]
            calculate_total_demand(rep_data, date_list, rep_id)

            if 'dealer' in levels:
                for dealer_id, dealer_name, _ in [x for x in dealer_id_maps if x[2] == rep_name]:
                    dealer_data = rep_data[rep_data['dealer'] == dealer_name]
                    calculate_total_demand(dealer_data, date_list, dealer_id)

                    if 'product_family' in levels:
                        for family_id, family_name, _, _ in [x for x in product_family_id_maps if x[2] == dealer_name and x[3] == rep_name]:
                            family_data = dealer_data[dealer_data['product_family'] == family_name]
                            calculate_total_demand(family_data, date_list, family_id)

                            if 'product_model' in levels:
                                for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if
                                                                      x[2] == family_name and x[3] == dealer_name and x[
                                                                          4] == rep_name]:
                                    model_data = family_data[family_data['product_model'] == model_name]
                                    calculate_total_demand(model_data, date_list, model_id)
                    elif 'product_model' in levels:
                        for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if
                                                              x[3] == dealer_name and x[4] == rep_name]:
                            model_data = dealer_data[dealer_data['product_model'] == model_name]
                            calculate_total_demand(model_data, date_list, model_id)
            elif 'product_family' in levels:
                for family_id, family_name, _, _ in [x for x in product_family_id_maps if x[3] == rep_name]:
                    family_data = rep_data[rep_data['product_family'] == family_name]
                    calculate_total_demand(family_data, date_list, family_id)

                    if 'product_model' in levels:
                        for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if
                                                              x[2] == family_name and x[4] == rep_name]:
                            model_data = family_data[family_data['product_model'] == model_name]
                            calculate_total_demand(model_data, date_list, model_id)
            elif 'product_model' in levels:
                for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if x[4] == rep_name]:
                    model_data = rep_data[rep_data['product_model'] == model_name]
                    calculate_total_demand(model_data, date_list, model_id)
    elif 'dealer' in levels:
        for dealer_id, dealer_name, rep_name in dealer_id_maps:
            dealer_data = demand_data[demand_data['dealer'] == dealer_name]
            calculate_total_demand(dealer_data, date_list, dealer_id)

            if 'product_family' in levels:
                for family_id, family_name, _, _ in [x for x in product_family_id_maps if x[2] == dealer_name]:
                    family_data = dealer_data[dealer_data['product_family'] == family_name]
                    calculate_total_demand(family_data, date_list, family_id)

                    if 'product_model' in levels:
                        for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if
                                                              x[2] == family_name and x[3] == dealer_name]:
                            model_data = family_data[family_data['product_model'] == model_name]
                            calculate_total_demand(model_data, date_list, model_id)
            elif 'product_model' in levels:
                for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if x[3] == dealer_name]:
                    model_data = dealer_data[dealer_data['product_model'] == model_name]
                    calculate_total_demand(model_data, date_list, model_id)
    elif 'product_family' in levels:
        for family_id, family_name, dealer_name, rep_name in product_family_id_maps:
            family_data = demand_data[demand_data['product_family'] == family_name]
            calculate_total_demand(family_data, date_list, family_id)

            if 'product_model' in levels:
                for model_id, model_name, _, _, _ in [x for x in product_model_id_maps if x[2] == family_name]:
                    model_data = family_data[family_data['product_model'] == model_name]
                    calculate_total_demand(model_data, date_list, model_id)
    elif 'product_model' in levels:
        for model_id, model_name, _, _, _ in product_model_id_maps:
            model_data = demand_data[demand_data['product_model'] == model_name]
            calculate_total_demand(model_data, date_list, model_id)

    # Overall demand
    for date_str in date_list:
        total_demand = demand_data[demand_data['date'] == date_str]['demand'].sum()
        result_data.append([0, date_str, total_demand])

    output_df = pd.DataFrame(result_data, columns=['id', 'date', 'total_demand'])

    # Pivot the data
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


# Example usage:
levels = ['region', 'product_model']  # Change this list to control the level of detail
result_df = calculate_demand_data(demand_data, levels)

# Output to Excel
output_file_path = 'C:/python_study/supply_chain_huawei/data/result.xlsx'  # Replace with your file path
result_df.to_excel(output_file_path, index=True, header=True)
print("Output saved to", output_file_path)

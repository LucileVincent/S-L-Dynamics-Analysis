# Data analysis of the database : NDC, CCDB and IFADV

import copy
import os
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

from snl_stats_extraction_data import *
from snl_stats_visualization_database import *
DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers = get_parameters()

################# parameters #####################
databases_name = [key.replace('_paths','').upper() for key in databases.keys()]
databases_pairs = [key for key in databases_pairs.keys()]
expressions = ["Smiles_0", "Laughs_0"]
# entities = {expression : tier_lists[expression] for expression in expressions}
laughs_intensities = tier_lists['Laughs_0']
smiles_intensities = tier_lists['Smiles_0']
delta = 1000
##################################################
for i in databases.keys():
    databases_list = databases_paths[i]
    for tier in expressions :
        combined_df = pd.DataFrame()
        added_columns = set() 
        filename_columns = []
        for role in tier_lists["Role"]:
            df = display_filtered_informations_by_entity(databases_list, i.replace('_paths',''), tier, tier_filter="Role", intensity_filter=role)
            new_columns = {col: f"{col}_for_{role}" for col in df.columns}
            df = df.rename(columns=new_columns)
            columns_to_add = [col for col in df.columns if col not in added_columns]
            if columns_to_add:
                df = df[columns_to_add]
                combined_df = pd.concat([combined_df, df], axis=1)
                added_columns.update(columns_to_add)
            filename_columns.extend([col for col in df.columns if col.startswith("Filename_")])
        filename_col_1 = combined_df[filename_columns[0]]
        filename_col_2 = combined_df[filename_columns[1]]

        if filename_col_1.hasnans:
            combined_df["Filename"] = filename_col_2
        else:
            combined_df["Filename"] = filename_col_1

        combined_df = combined_df.drop(columns=[filename_columns[0], filename_columns[1]])
        combined_df = combined_df.fillna(0)
        filename_column = combined_df.pop("Filename")
        combined_df.insert(0, "Filename", filename_column)
        
        display(Markdown(f"## {i.replace('_paths','').upper()} informations for {tier}:"))
        display(combined_df)
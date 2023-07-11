# Segments overlapping study
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
##################################################/
lstA = {}
lstB = {}
overlapping_segments_dict = {}
for i, database in enumerate(databases_name):
    if database == databases_pairs[i].replace('_pairs', '').upper():
        databases_list = databases_pair_paths[databases_pairs[i]]
        dataset_dict = {}
        for i in range(0, len(databases_list), 2):
            filepath_A = databases_list[i]
            filepath_B = databases_list[i+1]
            pair_name = f"Pair {i//2 + 1}"  
            pair_file_A = os.path.basename(filepath_A)
            pair_file_B = os.path.basename(filepath_B)

            if pair_file_A and pair_file_B:
                pair_name = f"Pair {pair_file_A}_&_{pair_file_B}"

            pair_dict = {}
            for tier in expressions + ["Role"]:
                lstA_tier = get_tier_from_file(filepath_A, tier)
                lstB_tier = get_tier_from_file(filepath_B, tier)

                if tier in lstA:
                    lstA[tier].extend(lstA_tier[tier])
                else:
                    lstA[tier] = lstA_tier[tier]

                if tier in lstB:
                    lstB[tier].extend(lstB_tier[tier])
                else:
                    lstB[tier] = lstB_tier[tier]

                overlapping_segments = get_overlapping_segments(lstA_tier[tier], lstB_tier[tier])
                print(overlapping_segments)
                pair_dict[tier] = {'Segments': overlapping_segments}

            dataset_dict[pair_name] = pair_dict

        overlapping_segments_dict[database] = dataset_dict
    
for database, dataset_dict in overlapping_segments_dict.items():
    print(f"Dataset: {database}")
    for pair_name, pair_dict in dataset_dict.items():
        print(f"Pair: {pair_name}")
        for tier, tier_dict in pair_dict.items():
            print(f"Tier: {tier}")
            segments = tier_dict['Segments']
            print(segments)
            print()
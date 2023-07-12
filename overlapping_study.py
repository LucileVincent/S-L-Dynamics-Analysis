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
##################################################
lstA = {}
lstB = {}
overlapping_segments_dict = {}
total_durations = []
for i, database in enumerate(databases_name):
    if database == databases_pairs[i].replace('_pairs', '').upper():
        databases_list = databases_pair_paths[databases_pairs[i]]
        dataset_dict = {}
        for i in range(0, len(databases_list), 2):
            filepath_A = databases_list[i]
            filepath_B = databases_list[i+1] 
            pair_file_A = os.path.basename(filepath_A)
            pair_file_B = os.path.basename(filepath_B)

            if pair_file_A and pair_file_B:
                pair_name = f"{pair_file_A}_&_{pair_file_B}"

            pair_dict = {}
            lstA_tier = get_tier_from_file(filepath_A, "Role")
            lstB_tier = get_tier_from_file(filepath_B, "Role")

            if "Role" in lstA:
                lstA["Role"].extend(lstA_tier["Role"])
            else:
                lstA["Role"] = lstA_tier["Role"]

            if "Role" in lstB:
                lstB["Role"].extend(lstB_tier["Role"])
            else:
                lstB["Role"] = lstB_tier["Role"]
            total_duration = 0
            for segA in lstA_tier["Role"]:
                if segA[2].replace(" ", "") == "spk":
                    total_duration += segA[1] - segA[0]
            total_durations.append(total_duration)
            overlapping_segments = get_overlapping_segments(lstA_tier["Role"], lstB_tier["Role"])
            pair_dict["Role"] = {'Segments': overlapping_segments}

            dataset_dict[pair_name] = pair_dict

        overlapping_segments_dict[database] = dataset_dict
print(total_durations)
dataframes = {}
i=0
for database, dataset_dict in overlapping_segments_dict.items():
    tiers = ["Role"]
    data = {tier: [] for tier in tiers}
    for pair_name, pair_dict in dataset_dict.items():
        for tier in tiers:
            segments = pair_dict[tier]['Segments']
            if not segments:
                overlap_duration = 0
                percentage = 0
            else:
                overlap_duration = 0
                for segmentA, segmentB in segments.items():
                    for seg in segmentB:
                        if seg[2].replace(" ", "") == "spk" and segmentA[2].replace(" ", "") == "spk":
                            if seg[0] > segmentA[0] and seg[1] < segmentA[1]:
                                overlap_duration += seg[1] - seg[0]
                            elif seg[0] < segmentA[0] and seg[1] > segmentA[1]:
                                overlap_duration += segmentA[1] - segmentA[0]
                            elif seg[0] < segmentA[0] and seg[1] < segmentA[1]:
                                overlap_duration += seg[1] - segmentA[0]
                            elif seg[0] > segmentA[0] and seg[1] > segmentA[1]:
                                overlap_duration += segmentA[1] - seg[0]
                percentage = overlap_duration / total_durations[i] * 100
            data[tier].append({
                'Pairs filenames': pair_name,
                'Overlap Percentage for speaker (%)': percentage,
                'Total Tier Duration for speaker (ms)': total_durations[i],
                'Overlap Duration for speaker (ms)': overlap_duration
            })
        i+=1
    dfs = []
    for tier in tiers:
        df = pd.DataFrame(data[tier])
        dfs.append(df)

    df_merged = pd.concat(dfs, axis=1)
    df_merged = df_merged.loc[:, ~df_merged.columns.duplicated()]
    df_filter = df_merged.filter(like='Overlap Percentage for')
    df_merged = df_merged.drop(df_filter.columns, axis=1)
    df_total = df_merged.sum(numeric_only=True)
    df_total['Pairs filenames'] = 'Total'

    for tier in ["Role"]:
        overlap_duration_col = 'Overlap Duration for speaker (ms)'
        total_duration_col = 'Total Tier Duration for speaker (ms)'
        overlap_percentage_col = 'Overlap Percentage for speaker (%)'
        df_total[overlap_percentage_col] = (df_total[overlap_duration_col] / df_total[total_duration_col]) * 100
    df_merged = pd.concat([df_merged, df_filter], axis=1)
    df_merged = pd.concat([df_merged, pd.DataFrame(df_total).T], ignore_index=True)
    dataframes[database] = df_merged

for database, df in dataframes.items():
    display(Markdown(f"**Database: {database}**"))
    display(df)
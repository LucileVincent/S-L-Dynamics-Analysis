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

def overlap_percentage_A(databases_name, databases_pairs, expression_pairs, expressions_track, choice):
    '''
    This function calculates the overlap percentage between two person for each pair of files.
    The total duration is calculated by adding the duration of the overlapping segments of the first person.
    When we talk about overlapping between person A to person B, this means that we are looking at all the 
    segments of person B which overlap a segment of A and this for all the segments of the tier concerned for 
    the "A" files. When we change direction (so person B to person A), we just switched the direction of the 
    files in the overlapping function. (A and B are the pair files)
        - person A to person B: {(segmentA: (segmentB n°1), (segmentB n°N), etc),...}
        - person B to person A: {(segmentB: (segmentA n°1), (segmentA n°N), etc),...}

    Args:
        databases_name: list of databases names.
        databases_pairs: list of databases pairs names.
        expression_pairs: list of expression pairs to study. For example : [("Smiles_0", "Smiles_0"), 
                                                                            ("Smiles_0", "Laughs_0"), 
                                                                            ("Laughs_0", "Laughs_0"), 
                                                                            ("Laughs_0", "Smiles_0")].
        expressions_track: list of expression pairs to study. For example : [("Smiles_0", "Smiles_0"),
                                                                            ("Smiles_0", "Laughs_0"),
                                                                            ("Laughs_0", "Laughs_0"),
                                                                            ("Laughs_0", "Smiles_0")].
        choice: chchoice between "A/B" or "B/A". For example : "A/B" for overlapping between person A to person B 
                or "B/A" for the opposite.
        
    Returns:
        dataframes: dictionary of dataframes containing the overlap percentage and duration for each pair of 
                    files.
    '''

    if choice == "A/B":
        person1 = "A"
        person2 = "B"
    elif choice == "B/A":
        person1 = "B"
        person2 = "A"

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
                pair_file_A = os.path.basename(filepath_A)
                pair_file_B = os.path.basename(filepath_B)

                if pair_file_A and pair_file_B:
                    if person1 == "A":
                        pair_name = f"{pair_file_A}_&_{pair_file_B}"
                    elif person1 == "B":
                        pair_name = f"{pair_file_B}_&_{pair_file_A}"
                pair_dict = {}
                overlapping_data = {}
                for tier_A, tier_B in expression_pairs:
                    lstA_tier = get_tier_from_file(filepath_A, tier_A)
                    lstB_tier = get_tier_from_file(filepath_B, tier_B)

                    if tier_A in lstA:
                        lstA[tier_A].extend(lstA_tier[tier_A])
                    else:
                        lstA[tier_A] = lstA_tier[tier_A]

                    if tier_B in lstB:
                        lstB[tier_B].extend(lstB_tier[tier_B])
                    else:
                        lstB[tier_B] = lstB_tier[tier_B]
                    
                    if person1 == "A":
                        overlapping_segments = get_overlapping_segments(lstA_tier[tier_A], lstB_tier[tier_B])
                        overlapping_data[f"{tier_A} vs {tier_B}"] = {'Segments': overlapping_segments}
                    elif person1 == "B":
                        overlapping_segments = get_overlapping_segments(lstB_tier[tier_B], lstA_tier[tier_A])
                        overlapping_data[f"{tier_B} vs {tier_A}"] = {'Segments': overlapping_segments}


                dataset_dict[pair_name] = overlapping_data

            overlapping_segments_dict[database] = dataset_dict

    dataframes = {}
    overlap_segments_set = set()
    for database, dataset_dict in overlapping_segments_dict.items():
        overlap_percentage_list = []
        for pair_name, pair_dict in dataset_dict.items():
            overlap_duration_spk_vs_lsn = 0
            overlap_duration_lsn_vs_spk = 0
            percentage_spk_vs_lsn = 0
            percentage_lsn_vs_spk = 0
            duration = 0
            segments = pair_dict["Role vs Role"]["Segments"]
            expression = expressions_track
            if person1 == "A":
                for segmentA, segmentB in segments.items():
                    for segB in segmentB:
                        segment_key = f"{segB}"
                        if segment_key not in overlap_segments_set:
                            overlap_segments_set.add(segment_key)
                            # Check if A is "spk" and B is "lsn"
                            if (segmentA[2].replace(" ", "") == "spk" and segB[2].replace(" ", "") == "lsn"):
                                for tierA, tierB in expression:
                                    segments_tier = pair_dict[f"{tierA} vs {tierB}"]["Segments"]   
                                    for A, B in segments_tier.items():
                                        if A[0] < segB[1] and A[1] > segB[0]:
                                            for b in B:
                                                if b[0] < segB[1] and b[1] > segB[0]:
                                                    tier_key = f"{b}"
                                                    if tier_key not in overlap_segments_set:
                                                        overlap_segments_set.add(tier_key)
                                                        duration += A[1] - A[0]
                                                        if b[0] > A[0] and b[1] < A[1]:
                                                            overlap_duration_spk_vs_lsn += b[1] - b[0]
                                                        elif b[0] < A[0] and b[1] > A[1]:
                                                            overlap_duration_spk_vs_lsn += A[1] - A[0]
                                                        elif b[0] < A[0] and b[1] < A[1]:
                                                            overlap_duration_spk_vs_lsn += b[1] - A[0]
                                                        elif b[0] > A[0] and b[1] > A[1]:
                                                            overlap_duration_spk_vs_lsn += A[1] - b[0]
                            # Check if A is "lsn" and B is "spk"
                            elif (segmentA[2].replace(" ", "") == "lsn" and segB[2].replace(" ", "") == "spk"):
                                for tierA, tierB in expression:
                                    segments_tier = pair_dict[f"{tierA} vs {tierB}"]["Segments"]   
                                    for A, B in segments_tier.items():
                                        if A[0] < segB[1] and A[1] > segB[0]:
                                            for b in B:
                                                if b[0] < segB[1] and b[1] > segB[0]:
                                                    tier_key = f"{b}"
                                                    if tier_key not in overlap_segments_set:
                                                        overlap_segments_set.add(tier_key)
                                                        duration += A[1] - A[0]
                                                        if b[0] > A[0] and b[1] < A[1]:
                                                            overlap_duration_lsn_vs_spk += b[1] - b[0]
                                                        elif b[0] < A[0] and b[1] > A[1]:
                                                            overlap_duration_lsn_vs_spk += A[1] - A[0]
                                                        elif b[0] < A[0] and b[1] < A[1]:
                                                            overlap_duration_lsn_vs_spk += b[1] - A[0]
                                                        elif b[0] > A[0] and b[1] > A[1]:
                                                            overlap_duration_lsn_vs_spk += A[1] - b[0]     
                        break
            elif person1 == "B": 
                for segmentB, segmentA in segments.items():
                    for segA in segmentA:
                        segment_key = f"{segA}"
                        if segment_key not in overlap_segments_set:
                            overlap_segments_set.add(segment_key)
                            # Check if B is "spk" and A is "lsn"
                            if (segmentB[2].replace(" ", "") == "spk" and segA[2].replace(" ", "") == "lsn"):
                                for tierB, tierA in expression:
                                    segments_tier = pair_dict[f"{tierB} vs {tierA}"]["Segments"]   
                                    for B, A in segments_tier.items():
                                        if B[0] < segA[1] and B[1] > segA[0]:
                                            for a in A:
                                                if a[0] < segA[1] and a[1] > segA[0]:
                                                    tier_key = f"{a}"
                                                    if tier_key not in overlap_segments_set:
                                                        overlap_segments_set.add(tier_key)
                                                        duration += B[1] - B[0]
                                                        if a[0] > B[0] and a[1] < B[1]:
                                                            overlap_duration_spk_vs_lsn += a[1] - a[0]
                                                        elif a[0] < B[0] and a[1] > B[1]:
                                                            overlap_duration_spk_vs_lsn += B[1] - B[0]
                                                        elif a[0] < B[0] and a[1] < B[1]:
                                                            overlap_duration_spk_vs_lsn += a[1] - B[0]
                                                        elif a[0] > B[0] and a[1] > B[1]:
                                                            overlap_duration_spk_vs_lsn += B[1] - a[0]
                            # Check if B is "lsn" and A is "spk"
                            elif (segmentB[2].replace(" ", "") == "lsn" and segA[2].replace(" ", "") == "spk"):
                                for tierB, tierA in expression:
                                    segments_tier = pair_dict[f"{tierB} vs {tierA}"]["Segments"]   
                                    for B, A in segments_tier.items():
                                        if B[0] < segA[1] and B[1] > segA[0]:
                                            for a in A:
                                                if a[0] < segA[1] and a[1] > segA[0]:
                                                    tier_key = f"{a}"
                                                    if tier_key not in overlap_segments_set:
                                                        overlap_segments_set.add(tier_key)
                                                        duration += B[1] - B[0]
                                                        if a[0] > B[0] and a[1] < B[1]:
                                                            overlap_duration_lsn_vs_spk += a[1] - a[0]
                                                        elif a[0] < B[0] and a[1] > B[1]:
                                                            overlap_duration_lsn_vs_spk += B[1] - B[0]
                                                        elif a[0] < B[0] and a[1] < B[1]:
                                                            overlap_duration_lsn_vs_spk += a[1] - B[0]
                                                        elif a[0] > B[0] and a[1] > B[1]:
                                                            overlap_duration_lsn_vs_spk += B[1] - a[0]       
                        break
            if duration != 0 :
                percentage_spk_vs_lsn = overlap_duration_spk_vs_lsn / (duration) * 100
                percentage_lsn_vs_spk = overlap_duration_lsn_vs_spk / (duration) * 100
            overlap_percentage_list.append({
                'Database': database,
                'Pair': pair_name,
                f'Overlap Duration for {person1} spk / {person2} lsn - S&L': overlap_duration_spk_vs_lsn,
                f'Overlap Percentage for {person1} spk / {person2} lsn - S&L': percentage_spk_vs_lsn,
                f'Overlap Duration for {person1} lsn / {person2} spk - S&L': overlap_duration_lsn_vs_spk,
                f'Overlap Percentage for {person1} lsn / {person2} spk - S&L': percentage_lsn_vs_spk,
            })
        df_overlap_percentage = pd.DataFrame(overlap_percentage_list)
        dataframes[database] = df_overlap_percentage
    return dataframes


expression_pairs = [("Smiles_0", "Smiles_0"), 
                    ("Smiles_0", "Laughs_0"), 
                    ("Laughs_0", "Laughs_0"), 
                    ("Laughs_0", "Smiles_0"), 
                    ("Role", "Role")]

expressions_track = [("Smiles_0", "Smiles_0"),
                    ("Smiles_0", "Laughs_0"),
                    ("Laughs_0", "Laughs_0"),
                    ("Laughs_0", "Smiles_0")]

df = overlap_percentage_A(databases_name, databases_pairs, expression_pairs, expressions_track, "A/B")
print(df)
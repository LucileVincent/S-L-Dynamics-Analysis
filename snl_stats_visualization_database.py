import os, sys

# script_path=os.path.realpath(os.path.dirname("IBPY"))
# os.chdir(script_path)
# sys.path.append("..")

from snl_stats_extraction_data import *
from IBPY.extract_data import *
from IBPY.visualization import *
DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers=get_parameters()

def display_general_informations_files(database):
    """ This function shows the general informations of the files.
    
    Args:
        database (list): list of all files paths
    Returns:
        list: list of tuples with the name of the file, the duration of the file and the number of tiers
    """
    lst=[]
    lst_time=get_time_eaf(database)
    lst_count=get_tier_count(database, tier_lists.keys())
    for i in range(len(database)):
        file_info=os.path.split(database[i])[-1], lst_time[i], *lst_count[i][:len(tier_lists.keys())]
        lst.append(file_info)
    return lst

def display_specific_informations(database, tier, intensities):
    """ This function shows the specific informations of the files filtered by a specific tier and entity.
    
    Args:
        database (list): list of all files paths
        tier (str): tier we search
        intensities (list): list of entities we search
    Returns:
        list: list of tuples with the name of the file, the duration of the file, the min time of the tier, the max time of the tier and the number of entities
    """
    lst=[]
    lst_tier_count=get_tier_intensities(database, tier, intensities)
    lst_min_time, lst_max_time=get_max_min_time_tier(database, tier)
    temp=[]
    for i in range(len(database)):
        for intensity in intensities:
            temp.append(lst_tier_count[i][intensity])
        file_info=os.path.split(database[i])[-1], lst_min_time[i], lst_max_time[i], *temp[:len(temp)]
        lst.append(file_info)
        temp.clear()
    return lst

def display_filtered_informations(listpaths, database, tier_list, tier_filter=None, intensity_filter=None):
    """ This function shows the general informations of the files filtered by a specific tier and intensity of this tier.
    
    Args:
        listpaths (list): List of folder file paths
        database (str): Name of the database
        tier_list (list): list of tiers to view
        tier_filter (str): Tier to filter
        intensity_filter (str): Intensity of the tier
    Returns:
        pd.DataFrame: DataFrame with filename, count of tier 1, count of tier 2, duration of tier 1, duration of tier 2
    """
    data = []
    columns = ['Filename', f'Count_{tier_list[0]}', f'Count_{tier_list[1]}', f'Duration_{tier_list[0]} (ms)', f'Duration_{tier_list[1]} (ms)']

    tier1_counts = []
    tier2_counts = []
    tier1_durations = []
    tier2_durations = []

    tier1_subjects = []
    for tier in tier_list:
        df = get_db_from_func_tier(DIR, eval("get_tier_from_tier"), database, tier_filter, tier, intensity_filter)
        grouped = df.groupby('subject')
        count = grouped['label'].count()
        duration = grouped['diff_time'].sum()

        if tier == tier_list[0]:
            tier1_counts = count
            tier1_durations = duration
            tier1_subjects = list(count.index)
        elif tier == tier_list[1]:
            tier2_counts = count
            tier2_durations = duration
            new_subjects = [subject for subject in count.index if subject not in tier1_subjects]
            tier1_subjects.extend(new_subjects)

    split_elements = []
    for element in listpaths:
        split_elements.append(os.path.split(element))

    for subject in tier1_subjects:
        filename = split_elements[int(subject) - 1][-1]
        count_tier1 = tier1_counts.get(subject, 0)
        count_tier2 = tier2_counts.get(subject, 0)
        duration_tier1 = tier1_durations.get(subject, 0)
        duration_tier2 = tier2_durations.get(subject, 0)
        
        # Replace missing values with 0
        if subject not in tier1_counts:
            count_tier1 = 0
            duration_tier1 = 0
        if subject not in tier2_counts:
            count_tier2 = 0
            duration_tier2 = 0

        # Check if the row is unique before appending to data
        if filename not in [row[0] for row in data]:
            data.append([filename, count_tier1, count_tier2, duration_tier1, duration_tier2])

    df = pd.DataFrame(data, columns=columns)
    return df

def display_filtered_informations_by_entity(listpaths, database, tier, tier_filter=None, intensity_filter=None):
    """ This function shows the general informations of the files filtered by a specific tier and intensity of this tier.
    
    Args:
        listpaths (list): List of folder file paths
        database (str): Name of the database
        tier (str): tier to view
        tier_filter (str): Tier to filter
        intensity_filter (str): Intensity of the tier
    Returns:
        pd.DataFrame: DataFrame with filename, count of tier 1, count of tier 2, duration of tier 1, duration of tier 2
    """
    data = []
    columns = [f'Filename_{tier}', f'Count_{tier}', f'Intensity_{tier}', f'Diff_time_{tier}']
    tier1_subjects = []

    df = get_db_from_func_tier(DIR, eval("get_tier_from_tier"), database, tier_filter, tier, intensity_filter)
    grouped = df.groupby('subject')
    split_elements = []
    for element in listpaths:
        split_elements.append(os.path.split(element))

    for subject, group_df in grouped:
        filename = split_elements[int(subject) - 1][-1]
        count_labels = group_df['label'].value_counts()

        for label, count_label in count_labels.items():
            diff_time = group_df.loc[group_df['label'] == label, 'diff_time'].sum()

            data.append([filename, count_label, label, diff_time])

    df = pd.DataFrame(data, columns=columns)
    return df


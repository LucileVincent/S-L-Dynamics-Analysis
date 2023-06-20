# Data analysis of the database : NDC, CCDB and IFADV

import copy
import os
import matplotlib.pyplot as plt

from snl_stats_extraction_data import *
DIR, databases_pair_paths, databases_paths, tier_lists, databases, databases_pairs, tiers = get_parameters()

################# parameters #####################
databases_name = [key.replace('_paths','').upper() for key in databases.keys()]
databases_pairs = [key for key in databases_pairs.keys()]
expressions = ["Smiles_0", "Laughs_0"]
# entities = {expression : tier_lists[expression] for expression in expressions}
laughs_intensities = tier_lists['Laughs_0']
smiles_intensities = tier_lists['Smiles_0']
delta = 0
##################################################

probabilities_matrix = []
moyenne_prob_interaction = 0
# Define the pairs of expressions for the heatmaps
expression_pairs = [("Smiles_0", "Smiles_0"), ("Smiles_0", "Laughs_0"), ("Laughs_0", "Laughs_0"), ("Laughs_0", "Smiles_0")]

# Iterate over the datasets
for dataset_index, database in enumerate(databases_name):
    # Create a new figure and axes for the current dataset
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 10), constrained_layout=True)
    
    # Track the current row and column index
    current_row = 0
    current_col = 0
    
    # Iterate over the expression pairs for the heatmaps
    for pair_index, (expression_choiceA, expression_choiceB) in enumerate(expression_pairs):
        # Get the appropriate intensity labels based on the expressions
        intensity_labelsT = copy.deepcopy(smiles_intensities) if expression_choiceA == "Smiles_0" else copy.deepcopy(laughs_intensities)
        intensity_labelsC = copy.deepcopy(smiles_intensities) if expression_choiceB == "Smiles_0" else copy.deepcopy(laughs_intensities)
        intensity_labelsC.append("null")
        
        # Create a 2x2 matrix with zeros
        probabilities_matrix_intensity = np.zeros((len(intensity_labelsT), len(intensity_labelsC)))
        
        list_mimicry_TC = expression_track_byI(expression_choiceA, expression_choiceB, DIR, [database], tier_lists)
        list_mimicry_TC_prev = list_mimicry_TC[0]  # Previous expression DataFrame
        list_mimicry_TC_next = list_mimicry_TC[1]  # Next expression DataFrame
        
        # Create the heatmap for combined expressions
        ax = axs[current_row, current_col]
        for i, intensityC in enumerate(intensity_labelsC):
            for j, intensityT in enumerate(intensity_labelsT):
                try :
                    filtered_list_prev = list_mimicry_TC_prev[
                        (list_mimicry_TC_prev['Intensityp'] == intensityC) &
                        (list_mimicry_TC_prev[f'Current_level_{expression_choiceB}p'] == intensityT)
                    ]
                    percentage_prev2 = filtered_list_prev['Percentagep'].values[0]
                    
                    filtered_list_next = list_mimicry_TC_next[
                        (list_mimicry_TC_next['Intensityf'] == intensityC) &
                        (list_mimicry_TC_next[f'Current_level_{expression_choiceB}f'] == intensityT)
                    ]
                    percentage_next2 = filtered_list_next['Percentagef'].values[0]
                    # Average the percentages for previous and next expressions
                    combined_percentage = (percentage_prev2 + percentage_next2) / 2
                    probabilities_matrix_intensity[i, j] = combined_percentage / 100.0
                except:
                    pass
                
        # Plot the heatmap
        im = ax.imshow(probabilities_matrix_intensity, cmap='YlGnBu', interpolation='nearest')
        # Add the text for each cell
        for i in range(len(intensity_labelsC)):
            for j in range(len(intensity_labelsT)):
                text = ax.text(i, j, f"{probabilities_matrix_intensity[j, i]:.5f}", ha='center', va='center', color='black')

        # Set the title for the current heatmap
        ax.set_xticks(range(len(intensity_labelsC)))
        ax.set_yticks(range(len(intensity_labelsT)))
        ax.set_xticklabels(intensity_labelsC)
        ax.set_yticklabels(intensity_labelsT)
        ax.set_xlabel(f"{expression_choiceA} (Check)")
        ax.set_ylabel(f"{expression_choiceB} (Track)")
        
        # Update the current row and column index
        current_col += 1
        if current_col == 2:
            current_row += 1
            current_col = 0
    
    # Add a common colorbar for the heatmaps of each database
    fig.colorbar(im, ax=axs, label='Probability')

    # Set the title for the figure based on the dataset
    fig.suptitle(f"Probabilities that smiles or laughs (columns) follow smiles or laughs (rows) at different intensities. for dataset: {database}", fontsize=16)
    
    # Show the figure
    plt.show()

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

probabilities_matrix_3 = []
moyenne_prob_interaction_3 = 0
# Define the pairs of expressions for the heatmaps
entity_pairs = [("spk", "lsn"), ("lsn", "spk")]

# Iterate over each database
for i, database in enumerate(databases_name):
    if database == databases_pairs[i].replace('_pairs', '').upper():
        databases_list = databases_pair_paths[databases_pairs[i]]

    # Create a new figure and axes
    fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(16, 10), constrained_layout=True)

    # Create a new dictionary to store entities grouped by expressions for each database
    entities_by_expression = {}

    # Group entities by expressions
    for expression_choiceA in expressions:
        entitiesA = tier_lists[expression_choiceA]
        for entityA in entitiesA:
            if expression_choiceA not in entities_by_expression:
                entities_by_expression[expression_choiceA] = []
            entities_by_expression[expression_choiceA].append(entityA)

    # Iterate over expression pairs and entities for each database
    for j, (expression_choiceA, entitiesA) in enumerate(entities_by_expression.items()):
        for k, (expression_choiceB, entitiesB) in enumerate(entities_by_expression.items()):
            # Create a matrix with zeros for spk and lsn categories
            num_entities_A = len(entitiesA)
            num_entities_B = len(entitiesB)
            probabilities_matrix_1 = np.zeros((num_entities_A, num_entities_B))
            probabilities_matrix_2 = np.zeros((num_entities_A, num_entities_B))

            # Track the current row and column index
            current_row = 0
            current_col = 0

            for entityA in entitiesA:
                for entityB in entitiesB:
                    for pair_index, (entity1, entity2) in enumerate(entity_pairs):
                        # Get the statistics for each entity of Role (spk or lsn)
                        list_mimicry_SL_by_role = give_mimicry_folder4(databases_list, database.lower(), get_tier_from_tier, get_tier_from_tier, expression_choiceA, expression_choiceB, 'Role', entity1=entity1, entity2=entity2, filter='Intensity', label=[str.lower(entityA), str.lower(entityB)], delta_t=delta)
                        moyenne_prob_interaction_3 = 0
                        for item in list_mimicry_SL_by_role:
                            moyenne_prob_interaction_3 += item[1]

                        moyenne_prob_interaction_3 /= len(list_mimicry_SL_by_role)

                        if entity1 == "spk":
                            probabilities_matrix_1[current_row, current_col] = moyenne_prob_interaction_3
                        elif entity1 == "lsn":
                            probabilities_matrix_2[current_row, current_col] = moyenne_prob_interaction_3

                    current_col += 1

                current_row += 1
                current_col = 0

            # Select the appropriate subplots for each heatmap
            ax_1 = axs[j, k * 2]
            ax_2 = axs[j, k * 2 + 1]

            # Create the heatmaps for spk and lsn
            im_spk = ax_1.imshow(probabilities_matrix_1, cmap='YlGnBu', interpolation='nearest')
            im_lsn = ax_2.imshow(probabilities_matrix_2, cmap='YlGnBu', interpolation='nearest')

            # Add the probability values within each square for spk and lsn
            for x in range(num_entities_A):
                for y in range(num_entities_B):
                    text_color_spk = 'black'
                    text_color_lsn = 'black'
                    ax_1.text(y, x, f'{probabilities_matrix_1[x, y]:.2f}', ha='center', va='center', color=text_color_spk)
                    ax_2.text(y, x, f'{probabilities_matrix_2[x, y]:.2f}', ha='center', va='center', color=text_color_lsn)

            # Customize the plots for spk
            ax_1.set_xticks(np.arange(num_entities_B))
            ax_1.set_xticklabels(entitiesB, rotation=90)
            ax_1.set_yticks(np.arange(num_entities_A))
            ax_1.set_yticklabels(entitiesA)
            ax_1.set_xlabel(f"{expression_choiceB} lsn")
            ax_1.set_ylabel(f"{expression_choiceA} spk")

            # Customize the plots for lsn
            ax_2.set_xticks(np.arange(num_entities_B))
            ax_2.set_xticklabels(entitiesB, rotation=90)
            ax_2.set_yticks(np.arange(num_entities_A))
            ax_2.set_yticklabels(entitiesA)
            ax_2.set_xlabel(f"{expression_choiceB} spk")
            ax_2.set_ylabel(f"{expression_choiceA} lsn")

    # Add a common colorbar for the heatmaps of each database
    fig.colorbar(im_spk, ax=axs, label='Probability')

    # Add a common title for the heatmaps of each database
    fig.suptitle(f'Mean mimicry probability heatmaps filtered by the role in the interaction for {database}', fontsize=16)

    # Show the plot
    plt.show()
                
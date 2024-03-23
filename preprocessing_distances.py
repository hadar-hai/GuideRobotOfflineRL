import pandas as pd
import useful_functions as uf
import os

# Loop over all the CSV files in the directory
data_input_directory = '.\processed_data\game_and_map_data'
data_output_directory = '.\processed_data\game_and_map_data_distances'
if data_output_directory not in os.listdir('.\processed_data'):
    os.mkdir(data_output_directory)
    
# Calculate distances
def calculate_distances(row):
    distances = []

    # Player 1 to Player 2
    p2_distance = uf.euclidean_distance(row['P1_X'], row['P1_Y'], row['P2_X'], row['P2_Y'])
    distances.append(p2_distance)

    # Calculate distances to all obstacles
    obstacle_distances2p1 = []
    obstacle_distances2p2 = []
    closest_points_to_p1 = []
    closest_points_to_p2 = []
    for obstacle_num in obstacle_nums:
        obs_x = row['obs_' + str(obstacle_num) + '_x']
        obs_y = row['obs_' + str(obstacle_num) + '_y']
        obs_height = row['obs_' + str(obstacle_num) + '_height']
        obs_width = row['obs_' + str(obstacle_num) + '_width']
        top_left, top_right, bottom_left, bottom_right = uf.calculate_corners(obs_x, obs_y, obs_width, obs_height)
        closest_points_to_p1.append(uf.closest_point_on_rectangle(top_left, top_right, bottom_left,
                                                        bottom_right, (row['P1_X'], row['P1_Y'])))
        closest_points_to_p2.append(uf.closest_point_on_rectangle(top_left, top_right, bottom_left,
                                                        bottom_right, (row['P2_X'], row['P2_Y']))) 
    closest_points_to_p1.sort(key=lambda x: uf.euclidean_distance(row['P1_X'], row['P1_Y'], x[0], x[1]))
    closest_points_to_p2.sort(key=lambda x: uf.euclidean_distance(row['P2_X'], row['P2_Y'], x[0], x[1]))
    
    # Calculate the distance to the closest 5 obstacles
    for i in range(5):
        obstacle_distances2p1.append(uf.euclidean_distance(row['P1_X'], row['P1_Y'], closest_points_to_p1[i][0], closest_points_to_p1[i][1]))
        obstacle_distances2p2.append(uf.euclidean_distance(row['P2_X'], row['P2_Y'], closest_points_to_p2[i][0], closest_points_to_p2[i][1])) 
    distances.extend(obstacle_distances2p1)
    distances.extend(obstacle_distances2p2)  
    # Distance to goal
    p1_goal_distance = uf.euclidean_distance(row['P1_X'], row['P1_Y'], row['goal_x'], row['goal_y'])
    p2_goal_distance = uf.euclidean_distance(row['P2_X'], row['P2_Y'], row['goal_x'], row['goal_y'])
    distances.append(p1_goal_distance)
    distances.append(p2_goal_distance)

    return pd.Series(distances)
    
for filename in os.listdir(data_input_directory):
    filename = filename.split('.')[0]
    # Load the data
    data = pd.read_csv(data_input_directory + "\\" + filename + ".csv")

    # Identify obstacle columns dynamically
    obstacle_cols = [col for col in data.columns if col.startswith('obs_')]
    obstacle_nums = [int(col.split('_')[1]) for col in obstacle_cols]
    obstacle_nums = list(set(obstacle_nums))

    # Apply the function to each row
    distances_df = data.apply(calculate_distances, axis=1)

    # Add timestamp column
    distances_df['P1_action'] = data['P1_Direction']
    distances_df['P2_action'] = data['P2_Direction']
    distances_df['reward'] = data['Total_Score']
    distances_df['timestamp_milliseconds'] = data['Elapsed_time_miliseconds']
    
    columns_titles = ['P1_to_P2_distance', 'P1_to_obs_1_distance', 'P1_to_obs_2_distance', 'P1_to_obs_3_distance', 
                    'P1_to_obs_4_distance', 'P1_to_obs_5_distance','P2_to_obs_1_distance', 'P2_to_obs_2_distance', 
                    'P2_to_obs_3_distance', 'P2_to_obs_4_distance', 'P2_to_obs_5_distance',
                    'P1_to_goal_distance', 'P2_to_goal_distance', 'P1_action', 'P2_action', 'reward', 'timestamp_milliseconds']

    distances_df.columns = columns_titles

    # Save the result to a new CSV file
    distances_df.to_csv(data_output_directory + "\\" + filename + "_distances_data.csv", index=False)
    print("Saved " + filename + "_distances_data.csv")
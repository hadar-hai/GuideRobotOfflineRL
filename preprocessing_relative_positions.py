import pandas as pd
import useful_functions as uf
import os



# Loop over all the CSV files in the directory
data_input_directory = '.\processed_data\game_and_map_data'
data_output_directory = '.\processed_data\game_and_map_data_relative_positions'
if data_output_directory not in os.listdir('.\processed_data'):
    os.mkdir(data_output_directory)

# Calculate relative positions
def calculate_relative_positions(row):
    relative_positions = []

    # Player 1 to Player 2
    p1_p2_relative_position = (row['P1_X'] - row['P2_X'], row['P1_Y'] - row['P2_Y'])
    relative_positions.append(p1_p2_relative_position)

    # Calculate distances to all obstacles
    obstacles2p1_relative_positions = []
    obstacles2p2_relative_positions = []
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
    
    # Add the relative positions from the 5 closest obstacles to each player
    for i in range(5):
        obstacles2p1_relative_positions.append((row['P1_X'] - closest_points_to_p1[i][0], row['P1_Y'] - closest_points_to_p1[i][1]))
        obstacles2p2_relative_positions.append((row['P2_X'] - closest_points_to_p2[i][0], row['P2_Y'] - closest_points_to_p2[i][1]))
    relative_positions.extend(obstacles2p1_relative_positions)
    relative_positions.extend(obstacles2p2_relative_positions)
                
    # Relative position to goal
    p1_goal_relative_position = (row['P1_X'] - row['goal_x'], row['P1_Y'] - row['goal_y'])
    p2_goal_relative_position = (row['P2_X'] - row['goal_x'], row['P2_Y'] - row['goal_y'])
    relative_positions.append(p1_goal_relative_position)
    relative_positions.append(p2_goal_relative_position)

    return pd.Series(relative_positions)
    
for filename in os.listdir(data_input_directory):
    filename = filename.split('.')[0]
    # Load the data
    data = pd.read_csv(data_input_directory + "\\" + filename + ".csv")

    # Identify obstacle columns dynamically
    obstacle_cols = [col for col in data.columns if col.startswith('obs_')]
    obstacle_nums = [int(col.split('_')[1]) for col in obstacle_cols]
    obstacle_nums = list(set(obstacle_nums))

    # Apply the function to each row
    relative_positions_df = data.apply(calculate_relative_positions, axis=1)

    # Add timestamp column
    relative_positions_df['timestamp_milliseconds'] = data['Elapsed_time_miliseconds']

    columns_titles = ['P1_to_P2_relative_position', 'P1_to_obs_1_relative_position', 'P1_to_obs_2_relative_position',
                      'P1_to_obs_3_relative_position', 'P1_to_obs_4_relative_position', 'P1_to_obs_5_relative_position'
                        ,'P2_to_obs_1_relative_position', 'P2_to_obs_2_relative_position', 'P2_to_obs_3_relative_position',
                        'P2_to_obs_4_relative_position', 'P2_to_obs_5_relative_position', 'P1_to_goal_relative_position',
                        'P2_to_goal_relative_position', 'timestamp_milliseconds']

    relative_positions_df.columns = columns_titles

    # Save the result to a new CSV file
    relative_positions_df.to_csv(data_output_directory + "\\" + filename + "_relative_positions_data.csv", index=False)
    print("Saved " + filename + "_relative_positions_data.csv")
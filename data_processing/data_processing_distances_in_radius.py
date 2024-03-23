import pandas as pd
import useful_functions as uf
import os

radius = 50

# Loop over all the CSV files in the directory
data_input_path = '.\processed_data\game_and_map_data'
data_output_path = '.\processed_data\game_and_map_data_distances_in_radius'
data_output_directory = data_output_path.split('\\')[-1]
if data_output_directory not in os.listdir('.\processed_data'):
    os.mkdir(data_output_path)

# calculate distances
def calculate_distances(row):
    distances = []

    # Player 1 to Player 2
    p2_distance = uf.euclidean_distance(row['P1_X'], row['P1_Y'], row['P2_X'], row['P2_Y'])
    distances.append(p2_distance)

    # Calculate distances to all obstacles
    # Initialize the lists with 50 None values
    obstacles2p1_distances = [None] * 50
    obstacles2p2_distances = [None] * 50
    points_in_p1_radius = []
    points_in_p2_radius = []
    for obstacle_num in obstacle_nums:
        obs_x = row['obs_' + str(obstacle_num) + '_x']
        obs_y = row['obs_' + str(obstacle_num) + '_y']
        obs_height = row['obs_' + str(obstacle_num) + '_height']
        obs_width = row['obs_' + str(obstacle_num) + '_width']
        top_left, top_right, bottom_left, bottom_right = uf.calculate_corners(obs_x, obs_y, obs_width, obs_height)
        # find all points on the rectangle that are within the radius of the player only if not empty:
        points_in_p1_radius_on_rectangular = uf.points_in_radius_on_rectangle(top_left, top_right, bottom_left, bottom_right, (row['P1_X'], row['P1_Y']), radius)
        if points_in_p1_radius_on_rectangular:
            a = 1
        points_in_p2_radius_on_rectangular = uf.points_in_radius_on_rectangle(top_left, top_right, bottom_left, bottom_right, (row['P2_X'], row['P2_Y']), radius)
        if points_in_p1_radius_on_rectangular:
            points_in_p1_radius.append(points_in_p1_radius_on_rectangular)
        if points_in_p2_radius_on_rectangular:
            points_in_p2_radius.append(points_in_p2_radius_on_rectangular)
    # reshape the list of lists to a single list
    points_in_p1_radius = [item for sublist in points_in_p1_radius for item in sublist]
    points_in_p2_radius = [item for sublist in points_in_p2_radius for item in sublist]
    # sort by distance 
    points_in_p1_radius.sort(key=lambda x: uf.euclidean_distance(row['P1_X'], row['P1_Y'], x[0], x[1]))
    points_in_p2_radius.sort(key=lambda x: uf.euclidean_distance(row['P2_X'], row['P2_Y'], x[0], x[1]))
    
    # Add the relative positions of the closest obstacles to the players, include up to 50 points
    num_points = min(50, len(points_in_p1_radius), len(points_in_p2_radius))
    for i in range(num_points):
        obstacles2p1_distances[i] = uf.euclidean_distance(row['P1_X'], row['P1_Y'], points_in_p1_radius[i][0], points_in_p1_radius[i][1])
        obstacles2p2_distances[i] = uf.euclidean_distance(row['P2_X'], row['P2_Y'], points_in_p2_radius[i][0], points_in_p2_radius[i][1])
    # Add the rest of points: 
    if num_points < 50:
        # If there are less than 50 points around p1 than around p2, continue adding points for p2
        if len(points_in_p1_radius) < len(points_in_p2_radius):
            for i in range(num_points + 1, min(50, len(points_in_p2_radius))):
                obstacles2p2_distances[i] = uf.euclidean_distance(row['P2_X'], row['P2_Y'], points_in_p2_radius[i][0], points_in_p2_radius[i][1])
        else: 
            for i in range(num_points + 1, min(50, len(points_in_p1_radius))):
                obstacles2p1_distances[i] = uf.euclidean_distance(row['P1_X'], row['P1_Y'], points_in_p1_radius[i][0], points_in_p1_radius[i][1])
    obstacles2p1_distances = [item for item in obstacles2p1_distances if item is not None]
    obstacles2p2_distances = [item for item in obstacles2p2_distances if item is not None]
    # replace large distances than '50' to '50'
    obstacles2p1_distances = [50 if x > 50 else x for x in obstacles2p1_distances]
    obstacles2p2_distances = [50 if x > 50 else x for x in obstacles2p2_distances]
    # pad the rest of the list with '50' value
    obstacles2p1_distances.extend([50] * (50 - len(obstacles2p1_distances)))
    obstacles2p2_distances.extend([50] * (50 - len(obstacles2p2_distances)))
    distances.extend(obstacles2p1_distances)
    distances.extend(obstacles2p2_distances)
                
    # Distance to goal
    p1_goal_distance = uf.euclidean_distance(row['P1_X'], row['P1_Y'], row['goal_x'], row['goal_y'])
    p2_goal_distance = uf.euclidean_distance(row['P2_X'], row['P2_Y'], row['goal_x'], row['goal_y'])
    distances.append(p1_goal_distance)
    distances.append(p2_goal_distance)

    return pd.Series(distances)
    
for filename in os.listdir(data_input_path):
    filename = filename.split('.')[0]
    # Load the data
    data = pd.read_csv(data_input_path + "\\" + filename + ".csv")

    # Identify obstacle columns dynamically
    obstacle_cols = [col for col in data.columns if col.startswith('obs_')]
    obstacle_nums = [int(col.split('_')[1]) for col in obstacle_cols]
    obstacle_nums = list(set(obstacle_nums))

    # Apply the function to each row
    distances_df = data.apply(calculate_distances, axis=1)

    # Add actions, reward and timestamp column
    distances_df['P1_action'] = data['P1_Direction']
    distances_df['P2_action'] = data['P2_Direction']
    distances_df['reward'] = data['Total_Score']
    distances_df['timestamp_milliseconds'] = data['Elapsed_time_miliseconds']

    columns_titles = ['P1_to_P2_distance']
    columns_titles.extend(['P1_to_obs_point_' + str(i) + '_distance' for i in range(50)])
    columns_titles.extend(['P2_to_obs_point_' + str(i) + '_distance' for i in range(50)])
    columns_titles.extend(['P1_to_goal_distance', 'P2_to_goal_distance', 'P1_action', 'P2_action', 'reward', 'timestamp_milliseconds'])

    distances_df.columns = columns_titles

    # Save the result to a new CSV file
    distances_df.to_csv(data_output_path + "\\" + filename + "_distances_in_radius_data.csv", index=False)
    print("Saved " + filename + "_distances_in_radius_data.csv")

import os 
import pandas as pd
# Load the data
data_input_path = '.\data\processed_data\game_and_map_data_distances_in_radius\\'
data_output_path = '.\data\processed_data\game_and_map_data_distances_in_radius_not_moving_actions_removed\\'
data_output_directory = data_output_path.split('\\')[-2]
if data_output_directory not in os.listdir('.\data\processed_data\\'):
    os.mkdir(data_output_path)

not_moving_action = 4 # 4 is the code for not moving

# Loop through all the files in the dataset
for filename in os.listdir(data_input_path):
    if filename.endswith(".csv"):
        # Read the file
        df = pd.read_csv(data_input_path + filename)
        # Remove the rows where the players are not moving
        df = df[(df['P1_action'] != not_moving_action)]
    else:
        continue
    # Save the file
    df.to_csv(data_output_path + filename, index=False)
    print(f"Saved {filename} to {data_output_path}")
    
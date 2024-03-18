import pandas as pd
import os

# Read the CSV file
data_input_directory = '.\processed_data\game_and_map_data_relative_positions\\'
data_output_directory = '.\processed_data\dataset\\'
if data_output_directory not in os.listdir('.\processed_data'):
    os.mkdir(data_output_directory)
    
first_file = os.listdir(data_input_directory)[0]
df = pd.read_csv(data_input_directory + first_file)
# s_columns is all except the 'P1_action','reward', 'timestamp_milliseconds' and without '_tag' columns
s_columns = [col for col in df.columns if col not in ['P1_action','reward', 'P2_action', 'timestamp_milliseconds'] and '_tag' not in col]

i = 0 
# Loop over all the CSV files in the directory
for filename in os.listdir(data_input_directory):
    # Load the data
    df = pd.read_csv(data_input_directory + filename)

    # Create columns for s and s_tag

    s = df[s_columns]
    s_tag = df[s_columns].shift(-1)
    s_tag = s_tag.rename(columns=lambda x: x + '_tag')

    # Extract action, reward, and timestamp
    a = df['P1_action']
    r = df['reward']
    t = df['timestamp_milliseconds']

    # Concatenate s and s_tag with a, r, and t
    dataset = pd.concat([s, s_tag, a, r, t], axis=1)

    # Save the result to a new CSV file
    filename = "dataset_" + str(i) + ".csv"
    dataset.to_csv(data_output_directory + filename, index=False)
    print("Saved " + filename)
    i += 1



    

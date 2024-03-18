import os
import pandas as pd

# Extract data from dataset 
data_input_directory = '.\processed_data\dataset\\'

firstfile = os.listdir(data_input_directory)[0]
df = pd.read_csv(data_input_directory + firstfile)
# s_columns is all except the 'P1_action','reward', 'timestamp_milliseconds' and without '_tag' columns
s_columns = [col for col in df.columns if col not in ['P1_action', 'P2_action', 'reward', 'timestamp_milliseconds'] and '_tag' not in col]

i = 0
datasets = {}
for filename in os.listdir(data_input_directory):
    # Load the data
    df = pd.read_csv(data_input_directory + filename)
    s = df[s_columns]
    s_tag = df[[col + '_tag' for col in s_columns]]
    a = df['P1_action']
    r = df['reward']
    t = df['timestamp_milliseconds']
    datasets[i] = [s, s_tag, a, r, t]
    i += 1

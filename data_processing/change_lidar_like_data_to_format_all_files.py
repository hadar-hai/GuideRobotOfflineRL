# Read this csv file format: P1_lidar_meas_in_0_deg	P1_lidar_meas_in_1_deg	P1_lidar_meas_in_2_deg	P1_lidar_meas_in_3_deg	P1_lidar_meas_in_4_deg	P1_lidar_meas_in_5_deg	P1_lidar_meas_in_6_deg	P1_lidar_meas_in_7_deg	P1_lidar_meas_in_8_deg
#[266.66666666666663, 'nothing', None]	[35.005331481536764, 'obstacle', (93, 115.38907272751239)]	[35.02133405045876, 'obstacle', (93, 114.77777306778884)]	[35.048032109927235, 'obstacle', (93, 114.16572772509356)]	[35.085466432841024, 'obstacle', (93, 113.55256158197714)]	[35.133694314017156, 'obstacle', (93, 112.93789677659267)]	[35.192789784723075, 'obstacle', (93, 112.32135176570132)]	[35.262843891059696, 'obstacle', (93, 111.70254036839833)]	[35.34396503815163, 'obstacle', (93, 111.0810707854163)]
#[266.66666666666663, 'nothing', None]	[35.005331481536764, 'obstacle', (93, 115.38907272751239)]	[35.02133405045876, 'obstacle', (93, 114.77777306778884)]	[35.048032109927235, 'obstacle', (93, 114.16572772509356)]	[35.085466432841024, 'obstacle', (93, 113.55256158197714)]	[35.133694314017156, 'obstacle', (93, 112.93789677659267)]	[35.192789784723075, 'obstacle', (93, 112.32135176570132)]	[35.262843891059696, 'obstacle', (93, 111.70254036839833)]	[35.34396503815163, 'obstacle', (93, 111.0810707854163)]
import pandas as pd
import os
import numpy as np
from multiprocessing import Pool

WIDTH = 800
HEIGHT = 600
RADIUS = 1/3*WIDTH

input_folder = 'data/processed_data/game_and_map_data_lidar_like_with_walls'
output_folder = 'data/processed_data/game_and_map_data_lidar_like_with_walls_arranged'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

lidar_measurements = []
labels = []
# for all files in the folder
for filename in os.listdir(input_folder):
    # read the csv file 
    data = pd.read_csv(input_folder + '/' + filename)
    for i, row in enumerate(data.iterrows()):
        final_row_flag = 0 if i < len(data) - 1 else 1
        lidar_measurement = []
        for angle in range(360):
            # extract the object type which is string, find it in the row
            object_type = row[1]['P1_lidar_meas_in_' + str(angle) + '_deg'].split(',')[1].split(',')[0].strip().replace("'", '')
            if object_type == 'nothing':
                bin_enc = [0,0,0,1]
            if object_type == 'obstacle':
                bin_enc = [0,0,1,0]
            if object_type == 'human':
                bin_enc = [0,1,0,0]
            if object_type == 'goal':
                bin_enc = [1,0,0,0]
            distance = float(row[1]['P1_lidar_meas_in_' + str(angle) + '_deg'].split(',')[0].split('[')[1].strip())
            # change to list 
            distance = [distance]
            # place the distance and bin_enc in the lidar_measurement list 
            lidar_measurement.extend([distance + bin_enc])
            # list to numpy array
        lidar_measurement = np.array(lidar_measurement)
        # flatten the numpy array
        lidar_measurement = lidar_measurement.flatten()
        # place the lidar_measurement array in the lidar_measurements array
        lidar_measurements.append(lidar_measurement)
        # add the final_row_flag to the lidar_measurement array
        lidar_measurements[-1] = np.append(lidar_measurements[-1], final_row_flag)
        # add file name to the lidar_measurement array
        lidar_measurements[-1] = np.append(lidar_measurements[-1], filename.split('.')[0].split('_lidar_like_data')[0])

    label = data['P1_action']
    # add file name to the labels
    label = label.to_frame()
    label['file_name'] = filename.split('.')[0].split('_lidar_like_data')[0]
    labels.append(label)
    print('Processed file: ', filename)


# create a new data frame with the lidar measurements
dataframe_lidar_meas = pd.DataFrame(lidar_measurements)
dataframe_labels = pd.concat(labels)
# change columns names to be more descriptive
# the first 5 columns are angle 0, the next 5 columns are angle 1, and so on
# the last column is the final_row_flag
columns = []
for i in range(360):
    for j in range(5):
        columns.append('angle_' + str(i) + '_distance_bin_enc_' + str(j))
columns.append('final_row_flag')
columns.append('file_name')
dataframe_lidar_meas.columns = columns

dataframe_labels.columns = ['P1_action', 'file_name']

# save the new data frame to a new csv file
dataframe_lidar_meas.to_csv(output_folder + '/lidar_like_data.csv', index=False)
dataframe_labels.to_csv(output_folder + '/labels.csv', index=False)

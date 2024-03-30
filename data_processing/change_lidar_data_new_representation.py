import pandas as pd
import os
import numpy as np
from multiprocessing import Pool

WIDTH = 800
HEIGHT = 600
RADIUS = round(1/3*WIDTH)

input_folder = 'smallmap_data/processed_data/game_and_map_data_lidar_like_with_walls'
original_folder = 'smallmap_data/processed_data/game_and_map_data'
output_folder = 'smallmap_data/processed_data/game_and_map_data_lidar'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

lidar_measurements = []
# for all files in the folder
for filename in os.listdir(input_folder):
    # read the csv file 
    data = pd.read_csv(input_folder + '/' + filename)
    data_2 = pd.read_csv(original_folder + '/' + filename.split('.')[0].split('_lidar_like_data')[0] + '.csv')
    
    
    for i, row in enumerate(data.iterrows()):
        final_row_flag = 0 if i < len(data) - 1 else 1
        dist = [data_2.iloc[i]['goal_x'] - data_2.iloc[i]['P1_X'], data_2.iloc[i]['goal_y'] - data_2.iloc[i]['P1_Y']]
        lidar_measurement = []
        for angle in range(360):
            # extract the object type which is string, find it in the row
            object_type = row[1]['P1_lidar_meas_in_' + str(angle) + '_deg'].split(',')[1].split(',')[0].strip().replace("'", '')
            distance = float(row[1]['P1_lidar_meas_in_' + str(angle) + '_deg'].split(',')[0].split('[')[1].strip())
            if object_type == 'nothing':
                bin_enc = [RADIUS, RADIUS, RADIUS]
            if object_type == 'obstacle':
                bin_enc = [RADIUS, RADIUS, distance]
            if object_type == 'human':
                bin_enc = [RADIUS, distance, RADIUS]
            if object_type == 'goal':
                bin_enc = [distance, RADIUS, RADIUS]
            # place the bin_enc in the lidar_measurement list 
            bin_enc =  np.array(bin_enc)    
            lidar_measurement = np.concatenate((lidar_measurement, bin_enc))
            # list to numpy array
            lidar_measurement = np.array(lidar_measurement)
            # flatten the numpy array
            lidar_measurement = lidar_measurement.flatten()
        
        dist = np.array(dist)
        lidar_measurement = np.concatenate((lidar_measurement, dist))
        lidar_measurement = lidar_measurement.flatten()
        # place the lidar_measurement array in the lidar_measurements array
        lidar_measurements.append(lidar_measurement)
        # add the final_row_flag to the lidar_measurement array
        lidar_measurements[-1] = np.append(lidar_measurements[-1], final_row_flag)
        # add file name to the lidar_measurement array
        lidar_measurements[-1] = np.append(lidar_measurements[-1], filename.split('.')[0].split('_lidar_like_data')[0])   
        # add the label 
        labels = np.array(data.iloc[i]['P1_action'])
        lidar_measurements[-1] = np.append(lidar_measurements[-1], labels)

    print('Processed file: ', filename)


# create a new data frame with the lidar measurements
dataframe_lidar_meas = pd.DataFrame(lidar_measurements)
print(dataframe_lidar_meas.shape)
# change columns names to be more descriptive
# the first 5 columns are angle 0, the next 5 columns are angle 1, and so on
# the last column is the final_row_flag
columns = []
for i in range(360):
    for j in range(3):
        columns.append('beam_' + "{:03d}".format(i) + '_dist_to_obj' + str(j))
columns.append('P1_goal_dist_x')
columns.append('P1_goal_dist_y')
columns.append('final_row_flag')
columns.append('file_name')
columns.append('P1_action')

dataframe_lidar_meas.columns = columns


# save the new data frame to a new csv file
dataframe_lidar_meas.to_csv(output_folder + '/lidar_like_data.csv', index=False)

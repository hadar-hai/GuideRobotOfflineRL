# Create labels file for the dataset
import os
import csv
import pandas as pd

dataset_path = "./processed_data/game_and_map_data/"
labels_path = "./dataset_labels/"

# Create one labels file for all datasets 
labels_filename = "labels.csv"
labels_file = open(labels_path + labels_filename, "w")
labels_writer = csv.writer(labels_file, lineterminator = '\n')
labels_writer.writerow(["dataset_game_frame", "label"])

# Loop through all the files in the dataset
for filename in os.listdir(dataset_path):
    if filename.endswith(".csv"):
        # Read the file
        df = pd.read_csv(dataset_path + filename)
        # Get the labels
        labels = df["P1_Direction"]
        # Write the labels to the labels file
        for i, label in enumerate(labels, start=1):
            dataset_game_frame = filename.split(".")[0] + "_frame_" + str(i)
            print(dataset_game_frame)
            # Write the label to the labels file
            labels_writer.writerow([dataset_game_frame, label])
    else:
        continue
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
import useful_functions as uf
import os
import pygame
import useful_functions as uf


dataset_path = "./processed_data/game_and_map_data/"
saving_path_videos = "./replaying_videos/"
saving_path_images = "./dataset_images/"
video_images_both_flag = "images"  # "both" or "video" or "images"


# Loop over all the CSV files in the directory
# Loop through all the files in the dataset
for filename in os.listdir(dataset_path):
    if filename.endswith(".csv"):
        filename = filename.split(".")[0]
        # Load the data
        data = pd.read_csv(".\processed_data\game_and_map_data\\" + filename + ".csv")
        if video_images_both_flag == "video" or video_images_both_flag == "both":
            if saving_path_videos.split('/')[-2] not in os.listdir('.'):
                os.mkdir(saving_path_videos)
            if saving_path_images.split('/')[-2] not in os.listdir('.'):
                os.mkdir(saving_path_images)
        elif video_images_both_flag == "images":
            if saving_path_images.split('/')[-2] not in os.listdir('.'):
                os.mkdir(saving_path_images)

        WIDTH = 800
        HEIGHT = 600

        # Identify obstacle columns dynamically
        obstacle_cols = [col for col in data.columns if col.startswith('obs_')]
        obstacle_nums = [int(col.split('_')[1]) for col in obstacle_cols]
        obstacle_nums = list(set(obstacle_nums))

        obstacles = []
        row = data.iloc[0]

        goal_x, goal_y = row['goal_x'], HEIGHT - row['goal_y']

        for obstacle_num in obstacle_nums:
            obs_x = row['obs_' + str(obstacle_num) + '_x']
            obs_y = row['obs_' + str(obstacle_num) + '_y']
            obs_height = row['obs_' + str(obstacle_num) + '_height']
            obs_width = row['obs_' + str(obstacle_num) + '_width']
            obstacle_rect = pygame.Rect(int(obs_x), HEIGHT - int(obs_y) - int(obs_height), int(obs_width), int(obs_height))
            obstacles.append(obstacle_rect)


        if video_images_both_flag == "video" or video_images_both_flag == "both":   
            # Create a VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'MP4V')
            video_out = cv2.VideoWriter(os.path.join(saving_path_videos, f"{filename}.mp4"), fourcc, 10.0, (WIDTH, HEIGHT))

        for i in range(len(data)):
            row = data.iloc[i]

            # Create a new figure
            plt.figure(figsize=(WIDTH/100, HEIGHT/100))

            # Plot the goal
            plt.scatter(goal_x, HEIGHT - goal_y, color='green', label='Goal')

            # Plot the obstacles
            for obstacle in obstacles:
                plt.gca().add_patch(Rectangle((obstacle.left, HEIGHT - obstacle.top - obstacle.height), obstacle.width, obstacle.height, color='black'))
                
            P1_X = row['P1_X']
            P1_Y = row['P1_Y']
            P2_X = row['P2_X']
            P2_Y = row['P2_Y']

            plt.scatter(P1_X, P1_Y, color='red', label='Robot')
            plt.scatter(P2_X, P2_Y, color='blue', label='Human')
            
            if uf.euclidean_distance(P1_X, P1_Y, P2_X, P2_Y) >= 50:
                plt.plot([P1_X, P2_X], [P1_Y, P2_Y], color='yellow')

            # Set plot limits and labels
            plt.xlim(0, WIDTH)
            plt.ylim(0, HEIGHT)
            # plt.grid(True)
            plt.gca().invert_yaxis()  # Invert y-axis to match the new orientation
            # plt.xlabel('X-coordinate')
            # plt.ylabel('Y-coordinate')
            # Print the game number
            # plt.title(file_name)
            # plt.legend()
            
            # Save the plot as an image
            image_file_name = filename + f"_frame_{i+1}.png"
            temp_img_path = os.path.join(saving_path_images, image_file_name)
            
            # show the frame number out of the total number of frames
            print(f"Frame {i+1}/{len(data)}")
            
            plt.savefig(temp_img_path)
            plt.close()
            
            if video_images_both_flag == "video" or video_images_both_flag == "both":
                # Read the image and write to the video
                img = cv2.imread(temp_img_path)
                video_out.write(img)

            # Remove temporary image file
            if video_images_both_flag == "video":
                os.remove(temp_img_path)
                
        if video_images_both_flag == "video" or video_images_both_flag == "both":
            # Release the VideoWriter object
            video_out.release()

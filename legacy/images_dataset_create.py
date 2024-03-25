import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pygame
import pandas as pd
import useful_functions as uf
import os

# Load the data
file_name = 'dataset_1_game_08'
data = pd.read_csv(".\processed_data\game_and_map_data\\" + file_name + ".csv")
saving_path = "./saved_images/"

WIDTH = 800
HEIGHT = 600

# Identify obstacle columns dynamically
obstacle_cols = [col for col in data.columns if col.startswith('obs_')]
obstacle_nums = [int(col.split('_')[1]) for col in obstacle_cols]
obstacle_nums = list(set(obstacle_nums))

obstacles = []
row = data.iloc[0]

goal_x, goal_y = row['goal_x'], HEIGHT - row['goal_y']

closest_points_to_p1 = []
for obstacle_num in obstacle_nums:
    obs_x = row['obs_' + str(obstacle_num) + '_x']
    obs_y = row['obs_' + str(obstacle_num) + '_y']
    obs_height = row['obs_' + str(obstacle_num) + '_height']
    obs_width = row['obs_' + str(obstacle_num) + '_width']
    obstacle_rect = pygame.Rect(int(obs_x), HEIGHT - int(obs_y) - int(obs_height), int(obs_width), int(obs_height))
    top_left, top_right, bottom_left, bottom_right = uf.calculate_corners(obs_x, obs_y, obs_width, obs_height)
    closest_points_to_p1.append(uf.closest_point_on_rectangle(top_left, top_right, bottom_left,
                                                              bottom_right, (row['P1_X'], row['P1_Y'])))
    obstacles.append(obstacle_rect)

for i in range(len(data)):
    row = data.iloc[i]
    # Plot the goal
    plt.scatter(goal_x, HEIGHT - goal_y, color='green', label='Goal')

    # Plot the obstacles
    for obstacle in obstacles:
        plt.gca().add_patch(
            Rectangle((obstacle.left, HEIGHT - obstacle.top - obstacle.height), obstacle.width, obstacle.height,
                      color='black'))
    plt.scatter(row['P1_X'], row['P1_Y'], color='red', label='Robot')
    plt.scatter(row['P2_X'], row['P2_Y'], color='blue', label='Human')

    # Set plot limits and labels
    plt.xlim(0, WIDTH)
    plt.ylim(0, HEIGHT)
    # plt.xlabel('X-coordinate')
    # plt.ylabel('Y-coordinate')
    # plt.title('Map with Obstacles, Goal, and Player Routes')
    # plt.legend()

    # Save plot as an image
    plt.savefig(os.path.join(saving_path, f"timestamp_{i+1}.png"))
    plt.close()

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pygame
import pandas as pd
import useful_functions as uf
import math

# Load the data
file_name = 'dataset_1_game_00'
file_name_processed_data = file_name + '_relative_positions_in_radius_data'
data = pd.read_csv(".\processed_data\game_and_map_data\\" + file_name + ".csv")
processed_data = pd.read_csv(".\processed_data\game_and_map_data_relative_positions_in_radius\\" + file_name_processed_data + ".csv")

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
    obstacles.append(obstacle_rect)

# Plot the goal
plt.scatter(goal_x, HEIGHT - goal_y, color='green', label='Goal')

# Plot the obstacles
for obstacle in obstacles:
    plt.gca().add_patch(Rectangle((obstacle.left, HEIGHT - obstacle.top - obstacle.height), obstacle.width, obstacle.height, color='black'))
    
player1_x = []
player1_y = []
player2_x = []
player2_y = []

# Read player routes from CSV file
for i in range(len(data)):
    row = data.iloc[i]
    player1_x.append(row['P1_X'])
    player1_y.append(row['P1_Y'])
    player2_x.append(row['P2_X'])
    player2_y.append(row['P2_Y'])
    
# # Plot player routes as points  
plt.scatter(player1_x, player1_y, label='Player 1 - Robot', color='red')
plt.scatter(player2_x, player2_y, label='Player 2 - Human', color='blue')

line = 1000

# Plot relative points based on relative positions only of the first row:
P1_to_obs_points = processed_data.iloc[line][[col for col in processed_data.columns if col.startswith('P1_to_obs')]]

# Calculate the points not relative to the player's first position
p1_x = float(data.iloc[line]['P1_X'])
p1_y = float(data.iloc[line]['P1_Y'])
for i in range(0, len(P1_to_obs_points), 2): 
    x_y = P1_to_obs_points[i]
    if isinstance(x_y, str) and x_y.strip() != "":
        x, y = eval(x_y)
        plt.scatter(p1_x - x, p1_y - y, color='yellow')

# plot a 50 radius circle around the player
circle = plt.Circle((p1_x, p1_y), 50, color='yellow', fill=False)
plt.gca().add_artist(circle)



# Set plot limits and labels
plt.xlim(0, WIDTH)
plt.ylim(0, HEIGHT)
plt.xlabel('X-coordinate')
plt.ylabel('Y-coordinate')
plt.title('Map with Obstacles, Goal, and Player Routes')
plt.legend()

# Show plot
plt.gca().invert_yaxis()  # Invert y-axis to match the new orientation
plt.grid(True)
plt.show()
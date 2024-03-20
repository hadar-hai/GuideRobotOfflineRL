import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pygame
import pandas as pd
import useful_functions as uf

# Load the data
file_name = 'dataset_1_game_08'
data = pd.read_csv(".\processed_data\game_and_map_data\\" + file_name + ".csv")

plot_extra_flag = False

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
    if plot_extra_flag:
        top_left, top_right, bottom_left, bottom_right = uf.calculate_corners(obs_x, obs_y, obs_width, obs_height)
        closest_points_to_p1.append(uf.closest_point_on_rectangle(top_left, top_right, bottom_left,
                                                            bottom_right, (row['P1_X'], row['P1_Y'])))
    obstacles.append(obstacle_rect)

# Plot the goal
plt.scatter(goal_x, HEIGHT - goal_y, color='green', label='Goal')

# Plot the obstacles
for obstacle in obstacles:
    plt.gca().add_patch(Rectangle((obstacle.left, HEIGHT - obstacle.top - obstacle.height), obstacle.width, obstacle.height, color='black'))
    if plot_extra_flag:
        # write on top of the obstacle its number
        plt.text(obstacle.left, HEIGHT - obstacle.top - obstacle.height, str(obstacles.index(obstacle)))
    
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
# plt.plot(player1_x, player1_y, label='Player 1 - Robot', color='red')
# plt.plot(player2_x, player2_y, label='Player 2 - Human', color='blue')


if plot_extra_flag:
    # plot the 5 closest points on obstacles to p1 in the first timestep
    for i in range(len(obstacles)):
        plt.scatter(closest_points_to_p1[i][0], closest_points_to_p1[i][1], color='red')
    row = data.iloc[0]
    # mark only the 5 closest 
    closest_points_to_p1.sort(key=lambda x: uf.euclidean_distance(row['P1_X'], row['P1_Y'], x[0], x[1]))
    for i in range(5):
        plt.scatter(closest_points_to_p1[i][0], closest_points_to_p1[i][1], color='yellow')
        # add a line between one point to p1
        plt.plot([row['P1_X'], closest_points_to_p1[i][0]], [row['P1_Y'], closest_points_to_p1[i][1]], color='yellow')
        # add the distance to the plot
        plt.text(closest_points_to_p1[i][0], closest_points_to_p1[i][1], str(round(uf.euclidean_distance(row['P1_X'], row['P1_Y'], closest_points_to_p1[i][0], closest_points_to_p1[i][1]), 2)))

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
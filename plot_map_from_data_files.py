import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pygame

map_data_file = 'map_data_00.csv'
game_data_file = 'game_data_00.csv'

WIDTH = 800
HEIGHT = 600

# Function to extract obstacle coordinates from the CSV row
def extract_obstacle_coords(row):
    obstacles = []
    for i in range(2, len(row), 4):  # Iterate over the obstacle columns with step 4
        if row[i] != '':
            obstacle_rect = pygame.Rect(int(row[i]), HEIGHT - int(row[i+1]) - int(row[i+3]), int(row[i+2]), int(row[i+3]))
            obstacles.append(obstacle_rect)
    return obstacles

# Read map data from CSV file and extract goal and obstacles
with open(map_data_file, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        goal_x, goal_y = int(row[0]), HEIGHT - int(row[1])
        obstacles = extract_obstacle_coords(row)

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
with open(game_data_file, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        player1_x.append(int(row[0]))
        player1_y.append(int(row[1]))
        player2_x.append(int(row[5]))
        player2_y.append(int(row[6]))

# Plot player routes
plt.plot(player1_x, player1_y, label='Player 1 - Robot', color='red')
plt.plot(player2_x, player2_y, label='Player 2 - Human', color='blue')

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

import csv
import matplotlib.pyplot as plt

map_data_file = './data/2024_02_21/dataset1/map_data_01.csv'
game_data_file = './data/2024_02_21/dataset1/game_data_01.csv'

# Function to extract obstacle coordinates from the CSV row
def extract_obstacle_coords(row):
    obstacles = []
    for i in range(2, len(row)):
        if row[i] != '':
            # Remove square brackets and split the string to get individual coordinates
            coords = row[i].strip('[]').split(',')
            obstacle = [int(coord) for coord in coords]
            obstacles.append(obstacle)
    return obstacles

# Read map data from CSV file and extract goal and obstacles
with open(map_data_file, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        goal_x, goal_y = int(row[0]), int(row[1])
        obstacles = extract_obstacle_coords(row)

# Plot the goal
plt.scatter(goal_x, goal_y, color='green', label='Goal')

# Plot the obstacles
for obstacle in obstacles:
    plt.rectangle = plt.Rectangle((obstacle[0], obstacle[1]), obstacle[2], obstacle[3], color='black')
    plt.gca().add_patch(plt.rectangle)

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
plt.xlim(0, 800)
plt.ylim(0, 600)
plt.xlabel('X-coordinate')
plt.ylabel('Y-coordinate')
plt.title('Map with Obstacles, Goal, and Player Routes')
plt.legend()

# Show plot
plt.grid(True)
plt.show()

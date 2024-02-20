import sys
import math
import random
import sys
import threading
import csv
import os
import datetime
import tkinter as tk
import pandas as pd
from tkinter import Tk, Label
import pygame

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
PLAYER_SIZE = 10
PLAYER_SPEED = 1
LEASH_MAX_LENGTH = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
FONT = pygame.font.Font(None, 36)

# Create the game window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Map Game")

def run_tkinter_gui(shared_instructions):
    def update_instruction():
        instruction = shared_instructions.get("instruction", "Ready")
        instruction_label.config(text=instruction)
        root.after(100, update_instruction)

    root = tk.Tk()
    root.title("Instructions for Player 2")
    instruction_label = tk.Label(root, text="Ready", font=("Helvetica", 24, "bold"))
    instruction_label.pack()
    update_instruction()
    root.mainloop()
shared_commands= {"instruction": "Ready"}



# Main_Player class
class Main_Player:
    def __init__(self, x, y, color=RED):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = color
        self.collision_flag = False
        self.reached_goal_flag = False  # Add a flag for reaching the goal


    def update_other_player(self, other_player: 'Secondary_Player' = None):
        self.other_player = other_player

    def draw(self):
        pygame.draw.circle(window, self.color, self.rect.center, PLAYER_SIZE // 2)

    def move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        if not any(obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2) for obstacle in
                   obstacles) and not any(
                obstacle.collides_with_line(new_rect.centerx, new_rect.centery, self.other_player.rect.centerx,
                                            self.other_player.rect.centery) for obstacle in obstacles):
            self.rect = new_rect
        else:
            self.collision_flag = True
            collision_text = FONT.render("Collision!", True, RED)
            window.blit(collision_text,
                        (WIDTH // 2 - collision_text.get_width() // 2, HEIGHT // 2 - collision_text.get_height() // 2))



# Secondary_Player class
class Secondary_Player:
    def __init__(self, x, y, color=BLUE):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = color
        self.collision_flag = False
        self.reached_goal_flag = False


    def update_other_player(self, other_player: 'Secondary_Player' = None):
        self.other_player = other_player

    def draw(self):
        pygame.draw.circle(window, self.color, self.rect.center, PLAYER_SIZE // 2)

    def move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        if not any(obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2) for obstacle in
                   obstacles) and not any(
                obstacle.collides_with_line(new_rect.centerx, new_rect.centery, self.other_player.rect.centerx,
                                            self.other_player.rect.centery) for obstacle in obstacles):
            self.rect = new_rect
        else:
            self.collision_flag = True
            collision_text = FONT.render("Collision!", True, RED)
            window.blit(collision_text,
                        (WIDTH // 2 - collision_text.get_width() // 2, HEIGHT // 2 - collision_text.get_height() // 2))




# Leash class
class Leash:
    def __init__(self, player1, player2, length):
        self.player1 = player1
        self.player2 = player2
        self.length = length

    def draw(self):
        pygame.draw.line(window, BLUE, self.player1.rect.center, self.player2.rect.center, 2)

    def update(self):
        # Calculate distance between players
        dist = math.sqrt((self.player1.rect.centerx - self.player2.rect.centerx) ** 2 +
                         (self.player1.rect.centery - self.player2.rect.centery) ** 2)
        return dist


# Obstacle class
class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.center = (x + width // 2, y + height // 2)

    def draw(self):
        pygame.draw.rect(window, BLACK, self.rect)

    def collides_with_circle(self, x, y, radius):
        # Calculate distance between obstacle's center and circle's center
        dist_x = abs(self.center[0] - x)
        dist_y = abs(self.center[1] - y)

        # If distance is greater than half the width or height of the obstacle, it's not colliding
        if dist_x > (self.rect.width / 2 + radius):
            return False
        if dist_y > (self.rect.height / 2 + radius):
            return False

        # If distance is less than half the width or height of the obstacle, it's colliding
        if dist_x <= (self.rect.width / 2):
            return True
        if dist_y <= (self.rect.height / 2):
            return True

        # Check collision with corner of the obstacle
        corner_dist_sq = (dist_x - self.rect.width / 2) ** 2 + (dist_y - self.rect.height / 2) ** 2
        return corner_dist_sq <= (radius ** 2)

    def collides_with_line(self, x1, y1, x2, y2):
        # Check if the line segment intersects with the obstacle
        line_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        if not line_rect.colliderect(self.rect):
            return False

        # Check each corner of the obstacle to see if it's on the line segment
        corners = [(self.rect.left, self.rect.top),
                   (self.rect.right, self.rect.top),
                   (self.rect.left, self.rect.bottom),
                   (self.rect.right, self.rect.bottom)]
        for corner in corners:
            if self.point_on_line_segment(corner[0], corner[1], x1, y1, x2, y2):
                return True

        # Check each side of the obstacle to see if it intersects with the line segment
        sides = [(self.rect.left, self.rect.top, self.rect.left, self.rect.bottom),
                 (self.rect.left, self.rect.top, self.rect.right, self.rect.top),
                 (self.rect.right, self.rect.top, self.rect.right, self.rect.bottom),
                 (self.rect.left, self.rect.bottom, self.rect.right, self.rect.bottom)]
        for side in sides:
            if self.segments_intersect(x1, y1, x2, y2, *side):
                return True

        return False

    def point_on_line_segment(self, x, y, x1, y1, x2, y2):
        return min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2)

    def segments_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        # Calculate the orientation of three points
        def orientation(px, py, qx, qy, rx, ry):
            val = (qy - py) * (rx - qx) - (qx - px) * (ry - qy)
            if val == 0:
                return 0
            return 1 if val > 0 else 2

        # Check if two line segments intersect
        o1 = orientation(x1, y1, x2, y2, x3, y3)
        o2 = orientation(x1, y1, x2, y2, x4, y4)
        o3 = orientation(x3, y3, x4, y4, x1, y1)
        o4 = orientation(x3, y3, x4, y4, x2, y2)

        if o1 != o2 and o3 != o4:
            return True

        # Special Cases
        if o1 == 0 and self.point_on_line_segment(x3, y3, x1, y1, x2, y2):
            return True
        if o2 == 0 and self.point_on_line_segment(x4, y4, x1, y1, x2, y2):
            return True
        if o3 == 0 and self.point_on_line_segment(x1, y1, x3, y3, x4, y4):
            return True
        if o4 == 0 and self.point_on_line_segment(x2, y2, x3, y3, x4, y4):
            return True

        return False

# Goal class
class Goal:
    def __init__(self, x, y, size=20, color=GREEN):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color

    def draw(self):
        pygame.draw.rect(window, self.color, self.rect)

class ScoreManager:
    def __init__(self):
        self.score = 100  # Initial score

    def update_score(self, player1, player2):
        if player1.collision_flag:
            self.score -= 40
            player1.collision_flag = False  # Reset flag after handling
        if player2.collision_flag:
            self.score -= 10
            player2.collision_flag = False  # Reset flag after handling
        if player1.reached_goal_flag or player2.reached_goal_flag:
            self.score += 100
            player1.reached_goal_flag = False  # Consider resetting these if you use them outside this logic
            player2.reached_goal_flag = False
        #self.score -= 1  # Subtract fixed reward for each time-step

    def get_score(self):
        return self.score

    def display_score(self, window, font):
        score_text = font.render(f"Score: {self.get_score()}", True, BLACK)
        window.blit(score_text, (10, 10))  # Position the score at the top-left corner

class GameData:
    def __init__(self, directory="C:/Users/anush/Downloads/gamedata"):
        self.directory = directory
        self.filename = self.generate_filename()
        self.filepath = os.path.join(self.directory, self.filename)

        # Ensure the directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Initialize the file with headers
        with open(self.filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            headers = ['P1_X', 'P1_Y', 'P1_Direction', 'P1_Crashed', 'P1_ReachedGoal',
                       'P2_X', 'P2_Y', 'P2_Direction', 'P2_Crashed', 'P2_ReachedGoal']
            writer.writerow(headers)

    def generate_filename(self):
        # Count the number of existing files to determine the next file name
        existing_files = [f for f in os.listdir(self.directory) if f.startswith("game_data_") and f.endswith(".csv")]
        next_file_number = len(existing_files)
        filename = f"game_data_{next_file_number:02d}.csv"
        return filename

    def update_state_vector(self, player1_state, player2_state):
        combined_state = player1_state + player2_state
        # Append the new state directly to the file
        with open(self.filepath, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(combined_state)

    def get_filepath(self):
        return self.filepath
def is_position_clear(x, y, size, obstacles):
    temp_rect = pygame.Rect(x, y, size, size)
    for obstacle in obstacles:
        if temp_rect.colliderect(obstacle.rect):
            return False
    return True

def place_entity_away_from_obstacles(entity_size, obstacles):
    while True:
        x = random.randint(0, WIDTH - entity_size)
        y = random.randint(0, HEIGHT - entity_size)
        if is_position_clear(x, y, entity_size, obstacles):
            return x, y
# Generate random obstacles
obstacles = []
NUM_OBSTACLES = 20
for _ in range(NUM_OBSTACLES):
    obstacle_width = random.randint(30, 100)
    obstacle_height = random.randint(30, 100)
    obstacle_x = random.randint(0, WIDTH - obstacle_width)
    obstacle_y = random.randint(0, HEIGHT - obstacle_height)
    obstacles.append(Obstacle(obstacle_x, obstacle_y, obstacle_width, obstacle_height))
for obstacle in obstacles:
        obstacle.draw()
robot_x, robot_y = place_entity_away_from_obstacles(PLAYER_SIZE, obstacles)

goal_x, goal_y = place_entity_away_from_obstacles(20, obstacles)  # Assuming the goal size is 20

player1 = Main_Player(robot_x, robot_y)
player2 = Secondary_Player(robot_x,robot_y, color=BLUE)
goal = Goal(goal_x, goal_y, size=20, color=GREEN)
player1.update_other_player(player2)
player2.update_other_player(player1)
leash = Leash(player1, player2, LEASH_MAX_LENGTH)



# Create the local environment window
local_env_width = LEASH_MAX_LENGTH * 2 + 50
local_env_height = LEASH_MAX_LENGTH * 2 + 50
local_env_window = pygame.Surface((local_env_width, local_env_height))



# Initialize the game data structure
game_data = GameData()
score_manager = ScoreManager()

# Main game loop
running = True
goal_reached = False


# Start the Tkinter thread
# Start Tkinter in a separate thread
tk_thread = threading.Thread(target=run_tkinter_gui, args=(shared_commands,))
tk_thread.daemon = True
tk_thread.start()
while running:
    window.fill(WHITE)
    # local_env_window.fill(WHITE)  # Clear the local environment window

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw()

    # Get the state of all keys
    keys = pygame.key.get_pressed()

    # Initialize movement deltas for both players
    dx_player1, dy_player1 = 0, 0
    dx_player2, dy_player2 = 0, 0
    direction_player1 = 4  # Stationary
    direction_player2 = 4  # Stationary

    # Player 1 Movement Input
    if keys[pygame.K_LEFT]:
        dx_player1 = -PLAYER_SPEED
        direction_player1 = 0  # Left
        shared_commands["instruction"] = "Move Left"
    elif keys[pygame.K_RIGHT]:
        dx_player1 = PLAYER_SPEED
        direction_player1 = 1  # Right
        shared_commands["instruction"] = "Move Right"
    elif keys[pygame.K_UP]:
        dy_player1 = -PLAYER_SPEED
        direction_player1 = 2  # Up
        shared_commands["instruction"] = "Move Up"
    elif keys[pygame.K_DOWN]:
        dy_player1 = PLAYER_SPEED
        direction_player1 = 3  # Down
        shared_commands["instruction"] = "Move Down"

    # Player 2 Movement Input
    if keys[pygame.K_a]:
        dx_player2 = -PLAYER_SPEED
        direction_player2 = 0  # Left
    elif keys[pygame.K_d]:
        dx_player2 = PLAYER_SPEED
        direction_player2 = 1  # Right
    elif keys[pygame.K_w]:
        dy_player2 = -PLAYER_SPEED
        direction_player2 = 2  # Up
    elif keys[pygame.K_s]:
        dy_player2 = PLAYER_SPEED
        direction_player2 = 3  # Down

    # Process player 2's movement first to allow player 1 to react to leash tension
    player2.move(dx_player2, dy_player2)

    # Now update the leash distance after player 2's movement
    leash_dist = leash.update()

    # Then decide on player 1's movement based on the leash's current state
    if leash_dist >= leash.length and (dx_player1 == -dx_player2 or dy_player1 == -dy_player2):
        # If the leash is taut and players are moving in opposite directions, player 1 follows player 2
        player1.move(dx_player2, dy_player2)
    else:
        # If the leash is not taut or no direct opposition in movement, proceed with player 1's intended movement
        player1.move(dx_player1, dy_player1)

    # Update leash distance once after all movements are processed
    leash_dist = leash.update()




    # Draw player 1, player 2, and leash
    player1.draw()
    player2.draw()
    leash.draw()

    # Draw the goal
    goal.draw()

    # Update the local environment rectangle around player 1
    local_env_rect = pygame.Rect(player1.rect.centerx - LEASH_MAX_LENGTH - 5,
                                 player1.rect.centery - LEASH_MAX_LENGTH - 5, local_env_width, local_env_height)

    # Check if the goal is in the local environment of the main player
    if not goal_reached and local_env_rect.colliderect(goal.rect):
        # Check if the goal is within 10 units of the main player
        distance_to_goal = math.sqrt(
            (player1.rect.centerx - goal.rect.centerx) ** 2 + (player1.rect.centery - goal.rect.centery) ** 2)
        if distance_to_goal <= LEASH_MAX_LENGTH:
            # End the game
            goal_reached = True
            print("You reached the goal!")
            player1.reached_goal_flag= True
            player2.reached_goal_flag= True
            goal_text = FONT.render("You reached the goal!", True, GREEN)
            window.blit(goal_text, (WIDTH // 2 - goal_text.get_width() // 2, HEIGHT // 2 - goal_text.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(5000)  # Wait for 5 seconds
    # Collision detection for player1 and player2
    player1_crashed = player1.collision_flag
    player2_crashed = player2.collision_flag

    # Update crash flags based on collision detection
    player1_crashed_b = 1 if player1_crashed else 0
    player2_crashed_b = 1 if player2_crashed else 0

    # Goal achievement check for player1
    player1_reached_goal = 1 if player1.reached_goal_flag else 0
    player2_reached_goal = 1 if player2.reached_goal_flag else 0

    # Example of updating game data for each player
    player1_state =[player1.rect.x, player1.rect.y, direction_player1, player1_crashed_b,
                                  player1_reached_goal]
    player2_state =[ player2.rect.x, player2.rect.y, direction_player2, player2_crashed_b,
                                  player2_reached_goal]

    # Increment timestep after each loop iteration
    # Update the game state vector
    game_data.update_state_vector(player1_state, player2_state)
    # Update the score based on current game state
    score_manager.update_score(player1, player2)
    score_manager.display_score(window, FONT)

    # # Draw local environment around player 1
    #local_env_window.blit(window, (0, 0), local_env_rect)  # Blit the portion of the main window onto the local environment window
    #pygame.draw.rect(local_env_window, GREEN, local_env_window.get_rect(), 2)  # Draw a border around the local environment window

    # # Draw the local environment window onto the main window
    # window.blit(local_env_window, (WIDTH - local_env_width - 10, HEIGHT - local_env_height - 10))

    # Update display
    pygame.display.update()

    # Check if the goal has been reached and exit the game after 5 seconds
    if goal_reached:
        pygame.time.wait(5000)  # Wait for 5 seconds
        running = False

    # Limit frames per second
    pygame.time.Clock().tick(30)

# Quit Pygame
pygame.quit()
sys.exit()


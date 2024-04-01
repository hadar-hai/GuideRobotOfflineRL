

import random
import threading
import math
import tkinter as tk
from PIL import Image
from PIL import ImageTk

from global_parameters import *
from Map_Features import Obstacle, Goal, ScoreManager
from Players import Main_Player, Secondary_Player, Leash
from DataStorage import *


class Game:

    def __init__(self, player1_agent = None, player2_agent = None, data_save_flag = False):
        # set agents
        # NOTE: if at least one of the agents it None, Game will assume both players are human and this is data collection.

        self.player1_agent = player1_agent  # robot actions. None = human player
        self.player2_agent = player2_agent # fake-human action. None = human player
        
        self.data_save_flag = data_save_flag
        self.leash_dist=0
        # initialize pygame
        pygame.init()
        self.font = pygame.font.Font(None, 36)

        # Create the game window
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2D Map Game")

        # Create obstacles
        self.obstacles = self.create_obstacles()

        # randomize initial location for the robot and the human
        self.robot_x, self.robot_y = self.place_entity_away_from_obstacles(PLAYER_SIZE, self.obstacles)

        # randomize initial location for the goal
        self.goal_x, self.goal_y = self.place_entity_away_from_obstacles(20, self.obstacles)  # Assuming the goal size is 20

        # save map data (obstacles, goal) to map file - this is done once
        if data_save_flag:
            self.map_data = MapData(self.obstacles, self.goal_x, self.goal_y)
            self.map_data.update_map_data()

        # Initialize players
        self.player1 = Main_Player(self.window, self.robot_x, self.robot_y, self.obstacles, color=RED, player_size=PLAYER_SIZE)
        self.player2 = Secondary_Player(self.window, self.robot_x, self.robot_y, self.obstacles, color=BLUE, player_size=PLAYER_SIZE)
        self.player1.update_other_player(self.player2)
        self.player2.update_other_player(self.player1)

        # Initialize Leash
        self.leash = Leash(self.window, self.player1, self.player2, LEASH_MAX_LENGTH)

        # Initialize goal
        self.goal = Goal(self.window, self.goal_x, self.goal_y, size=20, color=GREEN)

        # Initialize the game data structure
        if data_save_flag:
            self.game_data = GameData()
        self.score_manager = ScoreManager()

        # Set obstacles and goals to agents (if there are agents)
        if self.player1_agent:
            self.player1_agent.obstacles = self.obstacles
            self.player1_agent.goal = self.goal

        if self.player2_agent:
            self.player2_agent.obstacles = self.obstacles
            self.player2_agent.goal = self.goal

        # Start the Tkinter thread
        # Start Tkinter in a separate thread
        self.shared_commands = {"instruction": "Ready"}
        self.tk_thread = threading.Thread(target=self.run_tkinter_gui, args=(self.shared_commands,))
        self.tk_thread.daemon = True
        self.tk_thread.start()

    def quit_game(self):
        # Quit Pygame
        pygame.quit()
        # sys.exit()

    def game_loop(self, running=True, goal_reached = False):
        data_save_flag = self.data_save_flag
        while running:

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Fill the map in the current timestep:
            self.window.fill(WHITE)
            for obstacle in self.obstacles:
                obstacle.draw(self.window)

            # Set state
            player1_x = self.player1.rect.centerx
            player1_y = self.player1.rect.centery
            player2_x = self.player2.rect.centerx
            player2_y = self.player2.rect.centery
            self.current_state = [player1_x, player1_y, player2_x, player2_y]

            # # Get player input
            # if not (self.player1_agent and self.player2_agent):
            #     # If one of the agents is not defined - assume human input (data collections)
            #     dx1, dy1, direction_player1, dx2, dy2, direction_player2 = self.get_player_input()
            #
            # else:
            #     # Both agents are defined - choose action according to agent policy
            #     dx1, dy1, direction_player1 = self.player1_agent.get_state_set_action(self.current_state)
            #     dx2, dy2, direction_player2 = self.player2_agent.get_state_set_action(self.current_state)

            # Get player1 input
            if not self.player1_agent:
                dx1, dy1, direction_player1 = self.get_player1_input()
            else:
                dx1, dy1, direction_player1 = self.player1_agent.get_state_set_action(self.current_state)

            # Get player2 input
            if not self.player2_agent:
                dx2, dy2, direction_player2 = self.get_player2_input()
            else:
                dx2, dy2, direction_player2 = self.player2_agent.get_state_set_action(self.current_state)

            self.dx_player1 = dx1
            self.dy_player1 = dy1
            self.dx_player2 = dx2
            self.dy_player2 = dy2

            # move the players
            self.move_players()

            # Update leash distance once after all movements are processed
            self.leash_dist = self.leash.update()

            # Draw player 1, player 2 leash and goal
            self.player1.draw()
            self.player2.draw()
            self.leash.draw()
            self.goal.draw()

            # Check if goal is reached
            if self.reached_goal():
                running = False
                goal_reached = True
                pygame.time.wait(2000)  # Wait for 2 seconds

            # Check if human collided with obstacle - game over
            if self.player2.collision_flag:
                running = False
                goal_reached = False
                pygame.time.wait(2000)  # Wait for 2 seconds

            # Collision detection for player1 and player2
            player1_crashed = self.player1.collision_flag
            player2_crashed = self.player2.collision_flag

            # Update crash flags based on collision detection
            player1_crashed_b = 1 if player1_crashed else 0
            player2_crashed_b = 1 if player2_crashed else 0

            # Goal achievement check for player1
            player1_reached_goal = 1 if self.player1.reached_goal_flag else 0
            player2_reached_goal = 1 if self.player2.reached_goal_flag else 0

            # Example of updating game data for each player
            player1_state = [self.player1.rect.centerx, self.player1.rect.centery, direction_player1, player1_crashed_b,
                             player1_reached_goal]
            player2_state = [self.player2.rect.centerx, self.player2.rect.centery, direction_player2, player2_crashed_b,
                             player2_reached_goal]

            # Increment timestep after each loop iteration
            # Update the game state vector

            player1_score = self.score_manager.player1_score
            player2_score = self.score_manager.player2_score

            # Call update_state_vector with scores
            if data_save_flag:
                self.game_data.update_state_vector(player1_state, player2_state, player1_score, player2_score)
            # Update the score based on current game state
            self.score_manager.update_score(self.player1, self.player2)
            self.score_manager.display_score(self.window, self.font)

            # Update display
            pygame.display.update()

            # Limit frames per second
            pygame.time.Clock().tick(30)

        return goal_reached
    def reached_goal(self):
        goal_reached = False
        # Evaluate distance to goal
        distance_to_goal = math.sqrt(
            (self.player2.rect.centerx - self.goal.rect.centerx) ** 2 + (self.player2.rect.centery - self.goal.rect.centery) ** 2) # player 2 is the human player, distance to goal is calculated based on the human player's position

        if distance_to_goal <= GOAL_REACH_DISTANCE:
            # End the game
            goal_reached = True
            print("You reached the goal!")
            self.player1.reached_goal_flag = True
            self.player2.reached_goal_flag = True
            goal_text = self.font.render("You reached the goal!", True, GREEN)
            self.window.blit(goal_text, (WIDTH // 2 - goal_text.get_width() // 2, HEIGHT // 2 - goal_text.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(5000)  # Wait for 5 seconds

        return goal_reached

    def move_players(self):
        # Process player 2's movement first to allow player 1 to react to leash tension
        self.player2.move(self.dx_player2, self.dy_player2, self.font)

        # Update the leash distance after player 2's movement
        self.leash_dist = self.leash.update()
        next_leash_dist = math.sqrt(((self.player1.rect.centerx + self.dx_player1) - (self.player2.rect.centerx + self.dx_player2)) ** 2 +
                                    ((self.player1.rect.centery + self.dy_player1) - (self.player2.rect.centery + self.dy_player2)) ** 2)

        # Decide on player 1's movement based on the leash's current state

        if self.leash_dist >= self.leash.length:
            if next_leash_dist < self.leash_dist:
                # In that case, the robot moves to shorten the leash - this is ok.
                self.player1.move(self.dx_player1, self.dy_player1, self.font)
            else: #self.leash_dist >= self.leash.length and (dx_player1 == -dx_player2 or dy_player1 == -dy_player2):
                # If the leash is taut and players are moving in opposite directions, player 1 follows player 2
                self.player1.move(self.dx_player2, self.dy_player2, self.font)
        else:
            # If the leash is not taut or no direct opposition in movement, proceed with player 1's intended movement
            self.player1.move(self.dx_player1, self.dy_player1, self.font)

    def get_player1_input(self):
        # Get the state of all keys
        keys = pygame.key.get_pressed()

        # Initialize movement deltas for both players
        dx_player1, dy_player1 = 0, 0
        direction_player1 = 4  # Stationary

        # Player 1 Movement Input
        if keys[pygame.K_LEFT]:
            dx_player1 = -PLAYER_SPEED
            direction_player1 = 0  # Left
            self.shared_commands["instruction"] = "Move Left"
        elif keys[pygame.K_RIGHT]:
            dx_player1 = PLAYER_SPEED
            direction_player1 = 1  # Right
            self.shared_commands["instruction"] = "Move Right"
        elif keys[pygame.K_UP]:
            dy_player1 = -PLAYER_SPEED
            direction_player1 = 2  # Up
            self.shared_commands["instruction"] = "Move Up"
        elif keys[pygame.K_DOWN]:
            dy_player1 = PLAYER_SPEED
            direction_player1 = 3  # Down
            self.shared_commands["instruction"] = "Move Down"

        return dx_player1, dy_player1, direction_player1

    def get_player2_input(self):
        # Get the state of all keys
        keys = pygame.key.get_pressed()

        # Initialize movement deltas for both players
        dx_player2, dy_player2 = 0, 0
        direction_player2 = 4  # Stationary

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

        return dx_player2, dy_player2, direction_player2

    def get_player_input(self):
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
            self.shared_commands["instruction"] = "Move Left"
        elif keys[pygame.K_RIGHT]:
            dx_player1 = PLAYER_SPEED
            direction_player1 = 1  # Right
            self.shared_commands["instruction"] = "Move Right"
        elif keys[pygame.K_UP]:
            dy_player1 = -PLAYER_SPEED
            direction_player1 = 2  # Up
            self.shared_commands["instruction"] = "Move Up"
        elif keys[pygame.K_DOWN]:
            dy_player1 = PLAYER_SPEED
            direction_player1 = 3  # Down
            self.shared_commands["instruction"] = "Move Down"

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

        return dx_player1, dy_player1, direction_player1, dx_player2, dy_player2, direction_player2

    def create_obstacles(self):
        obstacles = []
        for _ in range(NUM_OBSTACLES):
            obstacle_width = random.randint(30, 100)
            obstacle_height = random.randint(30, 100)
            obstacle_x = random.randint(0, WIDTH - obstacle_width)
            obstacle_y = random.randint(0, HEIGHT - obstacle_height)
            obstacles.append(Obstacle(obstacle_x, obstacle_y, obstacle_width, obstacle_height))
        for obstacle in obstacles:
            obstacle.draw(self.window)
        return obstacles

    def is_position_clear(self, x, y, size, obstacles):
        '''
        A function that checks whether the position is clear, for collision detection.
        :param x: position x coordinate
        :param y: position y coordinate
        :param size: the size of the entity at the position
        :param obstacles: a list containing all obstacle objects in a given map
        :return: True if the position is clear, False otherwise
        '''
        temp_rect = pygame.Rect(x, y, size, size)
        for obstacle in obstacles:
            if temp_rect.colliderect(obstacle.rect):
                return False
        return True

    def place_entity_away_from_obstacles(self,entity_size, obstacles):
        '''
        Returns a random entity location that does not collide with an obstacle.
        :param entity_size: The size of the entity
        :param obstacles: list of map obstacle
        :return: entity location: x,y
        '''
        while True:
            x = random.randint(0, WIDTH - entity_size)
            y = random.randint(0, HEIGHT - entity_size)
            if self.is_position_clear(x, y, entity_size, obstacles):
                return x, y


    # Functions - tkinter GUI - fix later

    def run_tkinter_gui(self, shared_instructions):
        # Why is the nested function required?
        def update_instruction():
            # dx_player1 = self.dx_player1
            # dy_player1 = self.dy_player1
            # dx_player2 = self.dx_player2
            # dy_player2 = self.dy_player2
            # instruction = self.shared_commands.get("instruction", "Ready")
            if (self.leash_dist >= self.leash.length - 1): # and (dx_player1 == -dx_player2 or dy_player1 == -dy_player2)):
                # # Calculate leash direction angle
                leash_direction_angle = math.atan2(self.player1.rect.centery - self.player2.rect.centery,
                                                   self.player1.rect.centerx - self.player2.rect.centerx)
                # # Convert angle to degrees and rotate it 90 degrees clockwise to align with tkinter
                leash_direction_angle_deg = math.degrees(leash_direction_angle)
                # # Draw leash direction
                leash_direction = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.line(leash_direction, GREEN, (50, 50),
                                 (50 + int(math.cos(math.radians(leash_direction_angle_deg)) * 40),
                                  50 + int(math.sin(math.radians(leash_direction_angle_deg)) * 40)),
                                 5)  # Draw a line indicating leash direction

                # Convert pygame surface to PIL Image
                pil_image = Image.frombytes('RGBA', (100, 100), pygame.image.tostring(leash_direction, 'RGBA', False))

                # Convert PIL Image to Tkinter PhotoImage
                leash_direction_image = ImageTk.PhotoImage(pil_image)

                instruction_label.config(image=leash_direction_image)  # Set the PhotoImage as the label's image
                instruction_label.image = leash_direction_image  # Keep reference to prevent garbage collection
            else:
                empty_window = pygame.Surface((100, 100), pygame.SRCALPHA)
                # Convert pygame surface to PIL Image
                pil_image = Image.frombytes('RGBA', (100, 100), pygame.image.tostring(empty_window, 'RGBA', False))
                # Convert PIL Image to Tkinter PhotoImage
                empty_window_image = ImageTk.PhotoImage(pil_image)

                instruction_label.config(image=empty_window_image)  # Set the PhotoImage as the label's image
                instruction_label.image = empty_window_image  # Keep reference to prevent garbage collection

            # Schedule this function to be called again after 100 milliseconds
            root.after(1, update_instruction)

        root = tk.Tk()
        root.title("Instructions for Player 2")
        instruction_label = tk.Label(root, text="Ready", font=("Helvetica", 24, "bold"))
        instruction_label.pack()
        update_instruction()


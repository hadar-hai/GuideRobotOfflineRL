import random
from global_parameters import *
from math import sqrt
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
import useful_functions as uf
import os
import pygame
import time
from tensorflow.keras.models import load_model
import numpy as np
import cv2
from sklearn.preprocessing import StandardScaler
import math
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
import joblib
import LidarLikeNet
import LidarLikeNet01
from useful_functions_for_data_processing import UsefulFunctions_ForPreprocessing as uf_pp


class Agent:
    '''
    General agent class. Here we can modify agent inputs, outputs and general functions.
    Every agent should have a method called get_state_set_action
    '''

    def __init__(self, player_id, obstacles=None, goal=None):
        self.player_ID = player_id  # player 1 (robot) or player 2 (simulated human)
        self.obstacles = obstacles
        self.goal = goal

class BehavioralCloning_LidarBased_WithGoal_SuccesfulTrials(Agent):
    def __init__(self,  obstacles=None, goal=None):
            super().__init__(obstacles, goal)
            self.obstacles = obstacles
            self.goal = goal
            self.preprocessing = uf_pp()
            self.model_path = "checkpoints/model_checkpoint_LIDAR_succesfultrials_1.pth"
            self.model = None

    def initialize_model(self, input_dim):
            '''Initialize and load the model based on input_dim'''
            self.model = LidarLikeNet01.LidarLikeNet01(input_dim=input_dim, output_dim=5)  # Assuming output_dim=5

            self.model.load_state_dict(torch.load(self.model_path, map_location=torch.device('cpu')))
            self.model.eval()  # Set the model to evaluation mode

    def calculate_lidar_measurements(self, state=None, RADIUS=WIDTH * (1 / 3)):
        lidar_density = 1
        measurements = self.preprocessing.calculate_lidar_measurements(state, self.obstacles, self.goal,
                                                                       lidar_density=lidar_density, lidar_range=RADIUS)
        measurements = np.append(measurements, 0)
        return measurements

    def predict_action(self, state):
        measurements = self.calculate_lidar_measurements(state)
        measurements = np.ravel(measurements)
        P1_goal_dist_x = state[0] - self.goal.rect.centerx
        P1_goal_dist_y = state[1] - self.goal.rect.centery
        measurements = np.append(measurements, [P1_goal_dist_x, P1_goal_dist_y])


        self.initialize_model(input_dim=len(measurements))

        # Convert measurements to a PyTorch tensor
        x_tensor = torch.tensor([measurements], dtype=torch.float32)

        # Make predictions with the model
        with torch.no_grad():
            predictions = self.model(x_tensor)
        predicted_action = predictions.argmax(dim=1).item()
        return predicted_action

    def get_state_set_action(self, state=None):
        predicted_action = self.predict_action(state)
        dx, dy = 0, 0
        if predicted_action == 0:
            dx = -PLAYER_SPEED  # Left
        elif predicted_action == 1:
            dx = PLAYER_SPEED  # Right
        elif predicted_action == 2:
            dy = -PLAYER_SPEED  # Up
        elif predicted_action == 3:
            dy = PLAYER_SPEED  # Down
        return dx, dy, predicted_action


class BehavioralCloning_LidarBased_WithGoal(Agent):
    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)
        self.obstacles = obstacles
        self.goal = goal
        self.preprocessing = uf_pp()
        
    def calculate_lidar_measurements(self, state = None, RADIUS = WIDTH*(1/3)): 
        # All beams:
        lidar_density = 1
        # Less beams:
        # lidar_density = 10
        measurements = self.preprocessing.calculate_lidar_measurements(state, self.obstacles, self.goal, lidar_density = lidar_density, lidar_range = RADIUS)
        # plot lidar measurements for debugging:
        # self.preprocessing.plot_lidar_measurements_on_fig(measurements, state, self.obstacles, self.goal)
        return measurements
            
    def predict_action(self, state):
        # Calculate lidar measurements
        measurements = self.calculate_lidar_measurements(state)
        # Flatten the measurements
        measurements = np.ravel(measurements)
        # add the goal distances to the measurements
        P1_goal_dist_x = state[0] - self.goal.rect.centerx
        P1_goal_dist_y = state[1] - self.goal.rect.centery
        measurements = np.append(measurements, [P1_goal_dist_x, P1_goal_dist_y])
        input_dim = len(measurements)
        # All beams: 
        self.scaler_path = r".\data_based_agents\scalers\scaler_pytorch_without_not_moving_with_goal.pkl"
        self.model_path = r".\data_based_agents\models\behavior_cloning_lidar_pytorch_without_not_moving_with_goal.pth"
        # Less beams:
        # self.scaler_path = r".\data_based_agents\scalers\scaler_pytorch_without_not_moving_less_beams_with_goal.pkl"
        # self.model_path = r".\data_based_agents\models\behavior_cloning_lidar_pytorch_without_not_moving_less_beams_with_goal.pth"       
        # All beams, less epochs:
        # self.scaler_path = r".\data_based_agents\scalers\scaler_pytorch_without_not_moving_with_goal_less_epochs.pkl"
        # self.model_path = r".\data_based_agents\models\behavior_cloning_lidar_pytorch_without_not_moving_with_goal_less_epochs.pth"
        
        self.scaler = joblib.load(self.scaler_path)
        self.model = LidarLikeNet.LidarLikeNet(input_dim=input_dim, output_dim=5) 
        self.model.load_state_dict(torch.load(self.model_path))
        self.model.eval()
        


        # Normalize using the loaded scaler
        measurements = self.scaler.transform([measurements])
        # Convert to torch tensor
        x_tensor = torch.tensor(measurements, dtype=torch.float32)
        # Make predictions
        with torch.no_grad():
            predictions = self.model(x_tensor)
        # Get the predicted action
        predicted_action = predictions.argmax(dim=1).item()
        print("Predicted action: ", predicted_action)
        return predicted_action
    
    def get_state_set_action(self, state=None):
        '''
        :param state: positions of player 1 and player 2 (format?)
        :return: dx, dy, direction
        '''
        predicted_action = self.predict_action(state)

        dx, dy = 0, 0
        # return the action
        # defaults
        if predicted_action == 0:
            #left
            dx = -PLAYER_SPEED
        elif predicted_action == 1:
            #right
            dx = PLAYER_SPEED
        elif predicted_action == 2:
            #up
            dy = PLAYER_SPEED
        elif predicted_action == 3:
            #down
            dy = -PLAYER_SPEED
        action = predicted_action
        
        return dx, dy, action
class BehavioralCloning_LidarLikeTF(Agent):
    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)
        self.obstacles = obstacles
        self.goal = goal
        self.preprocessing = uf_pp()
    
    def calculate_lidar_measurements(self, state = None, RADIUS = WIDTH*(1/3)):  
        measurements = self.preprocessing.calculate_lidar_measurements(state, self.obstacles, self.goal, lidar_density = 1, lidar_range = RADIUS)
        return measurements    
    
    
    def get_state_set_action(self, state=None):
        
        measurements = self.calculate_lidar_measurements(state)
        model = load_model('.\data_based_agents\models\\behavior_cloning_lidar_tf.h5', compile=False)

        # Compile the model (recompilation is needed after loading)
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        # load the scaler
        scaler_path = r".\data\processed_data\scaler_tf.pkl"
        scaler = joblib.load(scaler_path)       
        # Convert to numpy array
        measurements = np.array(measurements)
        # Reshape the measurements
        measurements = measurements.reshape(-1, 1080)
        # Normalize the measurements
        measurements = scaler.transform(measurements)

        
        # Make predictions
        predictions = model.predict(measurements)
        predicted_action = int(np.argmax(predictions))

        dx, dy = 0, 0
        # return the action
        # defaults
        if predicted_action == 0:
            #left
            dx = -PLAYER_SPEED
        elif predicted_action == 1:
            #right
            dx = PLAYER_SPEED
        elif predicted_action == 2:
            #up
            dy = PLAYER_SPEED
        elif predicted_action == 3:
            #down
            dy = -PLAYER_SPEED
        action = predicted_action
        
        return dx, dy, action
        
        
class BehavioralCloning_LidarBased(Agent):
    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)
        self.obstacles = obstacles
        self.goal = goal
        self.preprocessing = uf_pp()

    
    def calculate_lidar_measurements(self, state = None, RADIUS = WIDTH*(1/3)):  
        measurements = self.preprocessing.calculate_lidar_measurements(state, self.obstacles, self.goal, lidar_density = 1, lidar_range = RADIUS)
        self.preprocessing.plot_lidar_measurements_on_fig(measurements, state, self.obstacles, self.goal)
        return measurements
             
    def predict_action(self, state):
        self.scaler_path = r".\data\processed_data\scaler_pytorch_without_not_moving.pkl"
        self.model_path = r".\data_based_agents\models\behavior_cloning_lidar_pytorch_without_not_moving.pth"
        # self.scaler_path = r".\data\processed_data\scaler_pytorch_without_not_moving_less_beams.pkl"
        # self.model_path = r".\data_based_agents\models\behavior_cloning_lidar_pytorch_without_not_moving_less_beams.pth"
        self.scaler = joblib.load(self.scaler_path)
        self.model = LidarLikeNet.LidarLikeNet(input_dim=1080, output_dim=5) # 1080
        self.model.load_state_dict(torch.load(self.model_path))
        self.model.eval()
        
        # Calculate lidar measurements
        measurements = self.calculate_lidar_measurements(state)
        # Flatten the measurements
        measurements = np.ravel(measurements)
        # Normalize using the loaded scaler
        measurements = self.scaler.transform([measurements])
        # Convert to torch tensor
        x_tensor = torch.tensor(measurements, dtype=torch.float32)
        # Make predictions
        with torch.no_grad():
            predictions = self.model(x_tensor)
        # Get the predicted action
        predicted_action = predictions.argmax(dim=1).item()
        print("Predicted action: ", predicted_action)
        return predicted_action
    
    def get_state_set_action(self, state=None):
        '''
        :param state: positions of player 1 and player 2 (format?)
        :return: dx, dy, direction
        '''
        predicted_action = self.predict_action(state)

        dx, dy = 0, 0
        # return the action
        # defaults
        if predicted_action == 0:
            #left
            dx = -PLAYER_SPEED
        elif predicted_action == 1:
            #right
            dx = PLAYER_SPEED
        elif predicted_action == 2:
            #up
            dy = PLAYER_SPEED
        elif predicted_action == 3:
            #down
            dy = -PLAYER_SPEED
        action = predicted_action
        
        return dx, dy, action
    
        
class BehavioralCloning_DistancesBasedAgent(Agent):
    def __init__(self, obstacles = None, goal = None, with_4_action = False):
        super().__init__(obstacles, goal)
        self.obstacles = obstacles
        self.goal = goal
        self.with_4_action = with_4_action
        
    def calculate_distances(self, state = None, radius = 50):
                # get player locations
        player1_x = state[0]
        player1_y = state[1]
        player2_x = state[2]
        player2_y = state[3]
        obstacles = self.obstacles
        goal = self.goal
        
        distances = []

        # Player 1 to Player 2
        p2_distance = uf.euclidean_distance(player1_x, player1_y, player2_x, player2_y)
        distances.append(p2_distance)

        # Calculate distances to all obstacles
        # Initialize the lists with 50 None values
        obstacles2p1_distances = [None] * 50
        obstacles2p2_distances = [None] * 50
        points_in_p1_radius = []
        points_in_p2_radius = []
        for obstacle in obstacles:
            obs_x = obstacle.rect.centerx
            obs_y = obstacle.rect.centery
            obs_height = obstacle.rect.height
            obs_width = obstacle.rect.width
            top_left, top_right, bottom_left, bottom_right = uf.calculate_corners(obs_x, obs_y, obs_width, obs_height)
            # find all points on the rectangle that are within the radius of the player only if not empty:
            points_in_p1_radius_on_rectangular = uf.points_in_radius_on_rectangle(top_left, top_right, bottom_left, bottom_right, (player1_x, player1_y), radius)
            if points_in_p1_radius_on_rectangular:
                a = 1
            points_in_p2_radius_on_rectangular = uf.points_in_radius_on_rectangle(top_left, top_right, bottom_left, bottom_right, (player2_x, player2_y), radius)
            if points_in_p1_radius_on_rectangular:
                points_in_p1_radius.append(points_in_p1_radius_on_rectangular)
            if points_in_p2_radius_on_rectangular:
                points_in_p2_radius.append(points_in_p2_radius_on_rectangular)
        # reshape the list of lists to a single list
        points_in_p1_radius = [item for sublist in points_in_p1_radius for item in sublist]
        points_in_p2_radius = [item for sublist in points_in_p2_radius for item in sublist]
        # sort by distance 
        points_in_p1_radius.sort(key=lambda x: uf.euclidean_distance(player1_x, player1_y, x[0], x[1]))
        points_in_p2_radius.sort(key=lambda x: uf.euclidean_distance(player2_x, player2_y, x[0], x[1]))
        
        # Add the relative positions of the closest obstacles to the players, include up to 50 points
        num_points = min(50, len(points_in_p1_radius), len(points_in_p2_radius))
        for i in range(num_points):
            obstacles2p1_distances[i] = uf.euclidean_distance(player1_x, player1_y, points_in_p1_radius[i][0], points_in_p1_radius[i][1])
            obstacles2p2_distances[i] = uf.euclidean_distance(player2_x, player2_y, points_in_p2_radius[i][0], points_in_p2_radius[i][1])
        # Add the rest of points: 
        if num_points < 50:
            # If there are less than 50 points around p1 than around p2, continue adding points for p2
            if len(points_in_p1_radius) < len(points_in_p2_radius):
                for i in range(num_points + 1, min(50, len(points_in_p2_radius))):
                    obstacles2p2_distances[i] = uf.euclidean_distance(player2_x, player2_y, points_in_p2_radius[i][0], points_in_p2_radius[i][1])
            else: 
                for i in range(num_points + 1, min(50, len(points_in_p1_radius))):
                    obstacles2p1_distances[i] = uf.euclidean_distance(player1_x, player1_y, points_in_p1_radius[i][0], points_in_p1_radius[i][1])
        obstacles2p1_distances = [item for item in obstacles2p1_distances if item is not None]
        obstacles2p2_distances = [item for item in obstacles2p2_distances if item is not None]
        # replace large distances than '50' to '50'
        obstacles2p1_distances = [50 if x > 50 else x for x in obstacles2p1_distances]
        obstacles2p2_distances = [50 if x > 50 else x for x in obstacles2p2_distances]
        # pad the rest of the list with '50' value
        obstacles2p1_distances.extend([50] * (50 - len(obstacles2p1_distances)))
        obstacles2p2_distances.extend([50] * (50 - len(obstacles2p2_distances)))
        distances.extend(obstacles2p1_distances)
        distances.extend(obstacles2p2_distances)
                    
        # Distance to goal
        p1_goal_distance = uf.euclidean_distance(player1_x, player1_y, goal.rect.centerx, goal.rect.centery)
        p2_goal_distance = uf.euclidean_distance(player2_x, player2_y, goal.rect.centerx, goal.rect.centery)
        distances.append(p1_goal_distance)
        distances.append(p2_goal_distance)

        return pd.Series(distances)    
        
    def get_state_set_action(self, state=None):
        '''
        :param state: positions of player 1 and player 2 (format?)
        :return: dx, dy, direction
        '''
        with_4_action = self.with_4_action
        distances = self.calculate_distances(state)

        # Load the model
        if with_4_action:
            model = load_model('.\data_based_agents\models\\behavior_cloning_distances.h5', compile=False)
        else:
            model = load_model('.\data_based_agents\models\\behavior_cloning_distances_not_moving_action_removed.h5', compile=False)

        # Compile the model (recompilation is needed after loading)
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        distances = distances.values.reshape(-1, 103)
        
        # Make predictions
        predictions = model.predict(distances)
        predicted_action = int(np.argmax(predictions))

        dx, dy = 0, 0
        # return the action
        # defaults
        if predicted_action == 0:
            #left
            dx = -PLAYER_SPEED
        elif predicted_action == 1:
            #right
            dx = PLAYER_SPEED
        elif predicted_action == 2:
            #up
            dy = PLAYER_SPEED
        elif predicted_action == 3:
            #down
            dy = -PLAYER_SPEED
        action = predicted_action
        
        return dx, dy, action

class BehavioralCloning_ImagesBasedAgent(Agent):
    def __init__(self, obstacles = None, goal = None, with_4_action = False):
        super().__init__(obstacles, goal)
        self.obstacles = obstacles
        self.goal = goal
        self.with_4_action = False
                
    def create_image(self, state):
        obstacles = self.obstacles
        goal = self.goal
        text_time = str(time.time())
        filename = text_time + ".png"
        saving_path_images = "./temp_images/"

        # create the folder if it does not exist
        if not os.path.exists(saving_path_images):
            os.makedirs(saving_path_images)

        goal_x, goal_y = goal.rect.centerx, HEIGHT - goal.rect.centery
        
        P1_X = state[0]
        P1_Y = state[1]
        P2_X = state[2]
        P2_Y = state[3]

        # Create a new figure
        plt.figure(figsize=(WIDTH/100, HEIGHT/100))

        # Plot the goal
        plt.scatter(goal_x, HEIGHT - goal_y, color='green', label='Goal')

        # Plot the obstacles
        for obstacle in obstacles:
            obstacle = obstacle.rect
            plt.gca().add_patch(Rectangle((obstacle.left, obstacle.top), obstacle.width, obstacle.height, color='black'))
            

        plt.scatter(P1_X, P1_Y, color='red', label='Robot')
        plt.scatter(P2_X, P2_Y, color='blue', label='Human')

        if uf.euclidean_distance(P1_X, P1_Y, P2_X, P2_Y) >= 50:
            plt.plot([P1_X, P2_X], [P1_Y, P2_Y], color='yellow')

        # Set plot limits and labels
        plt.xlim(0, WIDTH)
        plt.ylim(0, HEIGHT)
        plt.gca().invert_yaxis()  # Invert y-axis to match the new orientation
             
        temp_img_path = os.path.join(saving_path_images, filename)
        plt.savefig(temp_img_path)
        plt.close()
        return temp_img_path
    
    def get_state_set_action(self, state=None):
        '''
        :param state: positions of player 1 and player 2 (format?)
        :return: dx, dy, direction
        '''
        with_4_action = self.with_4_action
        # create image
        temp_img_path = self.create_image(state)
        # load image from temp_img_path
        image = cv2.imread(temp_img_path, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (100, 100))
        # Reshape X to match model input shape
        image = image.reshape(-1, 100, 100, 3)

        # Normalize pixel values to be between 0 and 1
        image = image.astype('float32') / 255.0

        # Load the model
        if with_4_action:
            model = load_model('.\data_based_agents\models\\behavior_cloning_cnn_100.h5', compile=False)
        else: 
            model = load_model('.\data_based_agents\models\\behavior_cloning_cnn_100_not_moving_action_removed.h5', compile=False)

        # Compile the model (recompilation is needed after loading)
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        # Make predictions
        predictions = model.predict(image)
        predicted_action = int(np.argmax(predictions[0]))
        
        # print the predicted action
        print("Predicted action: ", predicted_action)
        
        dx, dy = 0, 0
        # return the action
        # defaults
        if predicted_action == 0:
            #left
            dx = -PLAYER_SPEED
        elif predicted_action == 1:
            #right
            dx = PLAYER_SPEED
        elif predicted_action == 2:
            #up
            dy = PLAYER_SPEED
        elif predicted_action == 3:
            #down
            dy = -PLAYER_SPEED
        action = predicted_action
        
        # delete the image
        os.remove(temp_img_path)
        # wait for the process to finish
        time.sleep(0.5)
        return dx, dy, action
        
        
class RandomAgent(Agent):
    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)

    def get_state_set_action(self, state=None):
        '''
        :param state: positions of player 1 and player 2 (format?)
        :return: dx, dy, direction
        '''
        actions = [0, 1, 2, 3, 4]
        dx = 0
        dy = 0
        selected_action = random.choice(actions)

        if selected_action == 0:
            #left
            dx = -PLAYER_SPEED
        elif selected_action == 1:
            #right
            dx = PLAYER_SPEED
        elif selected_action == 2:
            #up
            dy = PLAYER_SPEED
        elif selected_action == 3:
            #down
            dy = -PLAYER_SPEED

        return dx, dy, selected_action

class EpsilonLeashFollow(Agent):
    # This agent makes a random step in the chance of epsilon,
    # Otherwise it follows the leash (if there is no leash signal it stays still).
    # This agent doesn't care which player_id it is, but only makes sense in replacing the human player!

    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)
        self.epsilon = 0.12
        self.no_of_steps = 3  # how many steps towards a taught leash
        self.current_state = None
        self.steps_remaining = 0

        # defaults
        self.dx = 0
        self.dy = 0
        self.action = 4

    def get_state_set_action(self, state=None):
        self.current_state = state
        # initialize action to noop
        dx = 0
        dy = 0
        action = 4


        # choose a random action in an epsilon chance
        if random.random() < self.epsilon:
            dx, dy, action = self.choose_random_action()
        else:
            # if there are steps remaining - continue moving in that direction
            if self.steps_remaining > 0:
                dx = self.dx  # from before
                dy = self.dy  # from before
                action = self.action  # from before
                self.steps_remaining = self.steps_remaining - 1
            else:
                if self.is_leash_at_max():
                    # if leash is at maximum length - follow it
                    self.steps_remaining = self.no_of_steps  # reset no of steps
                    dx, dy, action = self.follow_leash_direction()
                    self.dx = dx
                    self.dy = dy
                    self.action = action
                    pass
                else: # leash is not at max - don't move
                    pass
        return dx, dy, action

    def follow_leash_direction(self):
        # defaults
        dx = 0
        dy = 0
        action = 4

        # get player locations
        player1_x = self.current_state[0]
        player1_y = self.current_state[1]
        player2_x = self.current_state[2]
        player2_y = self.current_state[3]

        # determine which direction (up-down / left-right) is most dominant
        if abs(player1_x - player2_x) > abs(player1_y - player2_y):
            # x-axis is dominant - move right or left
            if player1_x < player2_x: # player 1 is more to the left - move left
                action = 0
                dx = -PLAYER_SPEED
            else: # move left
                action = 1
                dx = PLAYER_SPEED
        else:
            # y-axis is dominant - move up or down
            if player1_y > player2_y: # player 1 is higher - go up
                action = 2
                dy = PLAYER_SPEED
            else: #move down
                action = 3
                dy = -PLAYER_SPEED

        return dx, dy, action


    def is_leash_at_max(self):
        '''
        checks the state to see if the leas is at max
        :return: True or false
        '''
        leash_at_max = False

        # get player locations
        player1_x = self.current_state[0]
        player1_y = self.current_state[1]
        player2_x = self.current_state[2]
        player2_y = self.current_state[3]

        #calculate the distance between them:
        dist = sqrt((player1_x - player2_x)**2 + (player1_y-player2_y)**2)
        if dist >= LEASH_MAX_LENGTH:
            leash_at_max = True

        return leash_at_max


    def choose_random_action(self):
        '''
        chooses a random action
        :return: dx, dy, selected action
        '''
        actions = [0, 1, 2, 3, 4]
        dx = 0
        dy = 0
        action = 4  # noop = default
        selected_action = random.choice(actions)

        if selected_action == 0:
            # left
            dx = -PLAYER_SPEED
        elif selected_action == 1:
            # right
            dx = PLAYER_SPEED
        elif selected_action == 2:
            # up
            dy = PLAYER_SPEED
        elif selected_action == 3:
            # down
            dy = -PLAYER_SPEED

        return dx, dy, selected_action

class Roomba(Agent):
    # This agent picks a random direction and makes a finite amount of steps in that direction
    def __init__(self, obstacles=None, goal=None):
        super().__init__(obstacles, goal)
        self.max_steps = 100
        self.steps_remaining = 0
        self.current_action = 4 # default
        self.dx = 0
        self.dy = 0

    def get_state_set_action(self, state=None):
        action = 4
        dx = 0
        dy = 0

        if self.steps_remaining > 0:
            # if there are steps remaining - continue moving where you were
            dx = self.dx
            dy = self.dy
            action = self.current_action

            self.steps_remaining = self.steps_remaining - 1

        else:
            # otherwise - randomize direction and move
            self.steps_remaining = self.max_steps

            directions = [0, 1, 2, 3]
            action = random.choice(directions)

            if action == 0:
                # left
                dx = -PLAYER_SPEED
            elif action == 1:
                # right
                dx = PLAYER_SPEED
            elif action == 2:
                # up
                dy = PLAYER_SPEED
            elif action == 3:
                # down
                dy = -PLAYER_SPEED

            self.current_action = action
            self.dx = dx
            self.dy = dy

        return dx, dy, action

class GoalFollow(Agent):
    # This robot agent goes in the direction of the goal.
    # if this robot collides with an obstacle - it escapes it
    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)
        self.is_escaping_obstacle = False
        self.escape_action = 4
        self.escape_dx = 0
        self.escape_dy = 0

        self.obstacles = obstacles
        self.goal = goal

    def get_state_set_action(self, state=None):
        self.current_state = state

        # defaults
        action = 4
        dx = 0
        dy =0

        self.player1_x = state[0]

        if self.is_escaping_obstacle:
            # if we are in an obstacle escape sequence - move
            action = self.escape_action
            dx = self.escape_dx
            dy = self.escape_dy
        else:
            if self.collision_detection():
                # if we are colliding with obstacle - initiate escape
                self.is_escaping_obstacle = True
                dx, dy, action = self.choose_random_action()
                self.escape_action = action
                self.escape_dx = dx
                self. escape_dy = dy
            else:
                # else: move in the direction of the goal
                dx, dy, action = self.move_to_goal()

        return dx, dy, action

    def move_to_goal(self):
        '''
        chooses an action and direction based on where the target and player 2 (human) are.
        :return: dx, dy, action
        '''
        # defaults
        action = 4
        dx = 0
        dy = 0

        # get player and goal positions
        player2_x = self.current_state[2]
        player2_y = self.current_state[3]
        goal_x = self.goal.rect.centerx
        goal_y = self.goal.rect.centery

        # determine which axis is stronger - up/down or left\right
        if abs(player2_x-goal_x) > abs(player2_y-goal_y):
            # move left or right
            if goal_x < player2_x: #goal is to the left - move left
                action = 0
                dx = -PLAYER_SPEED
            else: #goal is to the right - move right
                action = 1
                dx = PLAYER_SPEED
        else:
            # move up or down
            if goal_y > player2_y: #goal is upwards - move up
                action = 2
                dy = PLAYER_SPEED
            else: #goal is downwards - move down
                action = 3
                dy = -PLAYER_SPEED

        return dx, dy, action



    def collision_detection(self):
        '''
        check for collision of the robot agent (player 1)
        :return: True or False
        '''

        # get player locations
        player1_x = self.current_state[0]
        player1_y = self.current_state[1]

        temp_rect = pygame.Rect(player1_x, player1_y, PLAYER_SIZE, PLAYER_SIZE)
        for obstacle in self.obstacles:
            if temp_rect.colliderect(obstacle.rect):
                return True

        return False

    def choose_random_action(self):
        '''
        chooses a random action
        :return: dx, dy, selected action
        '''
        actions = [0, 1, 2, 3]
        dx = 0
        dy = 0
        action = 4  # noop = default
        selected_action = random.choice(actions)

        if selected_action == 0:
            # left
            dx = -PLAYER_SPEED
        elif selected_action == 1:
            # right
            dx = PLAYER_SPEED
        elif selected_action == 2:
            # up
            dy = PLAYER_SPEED
        elif selected_action == 3:
            # down
            dy = -PLAYER_SPEED

        return dx, dy, selected_action

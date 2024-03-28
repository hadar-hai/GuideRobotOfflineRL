import pygame
import math
import useful_functions as uf
from global_parameters import *
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# Define the class for the useful functions
class UsefulFunctions_ForPreprocessing:
    def __init__(self):
        self.intersection_point = None
        self.intersection_label = None
        self.min_distance = float('inf')
        self.angle_rad = None
        
    def check_if_obj_in_path(self, human_or_goal = None):
        angle_rad = self.angle_rad
        lidar_range = self.lidar_range
        p1_x = self.p1_x
        p1_y = self.p1_y
        p2_x = self.p2_x
        p2_y = self.p2_y
        goal_x = self.goal_x
        goal_y = self.goal_y
        
        if human_or_goal == 'goal':
            x = goal_x
            y = goal_y
        elif human_or_goal == 'human':
            x = p2_x
            y = p2_y
    
        angle_to_obj = math.atan2(y - p1_y, x - p1_x)
        if angle_to_obj < 0:
            angle_to_obj += 2 * math.pi
        if abs(angle_to_obj - angle_rad) < math.radians(1):
            distance = uf.euclidean_distance(p1_x, p1_y, x, y)
            if distance < self.min_distance and distance < lidar_range:
                self.min_distance = distance
                self.intersection_point = (x, y)
                self.intersection_label = human_or_goal
                
        return self.min_distance, self.intersection_point, self.intersection_label
        
    def check_if_obstacle_in_path(self, obstacle = None, ray_x = None, ray_y = None):
        
        angle_rad = self.angle_rad
        min_distance = self.min_distance
        intersection_point = self.intersection_point
        intersection_label = self.intersection_label
        lidar_range = self.lidar_range
        
        top_left_y = obstacle.rect.top
        top_left_x = obstacle.rect.left
        bottom_right_y = obstacle.rect.bottom
        bottom_right_x = obstacle.rect.right
        
        p1_x = self.p1_x
        p1_y = self.p1_y
        
        # if the obstacle is not in the ray's direction continue
        angle = math.degrees(angle_rad)
        if ((0 < angle < 180) and (top_left_y < p1_y) and (bottom_right_y < p1_y)) or ((180 < angle < 360) and (top_left_y > p1_y) and (bottom_right_y > p1_y)):
            # don't return anything
            return min_distance, intersection_point, intersection_label
        if ((90 < angle < 270) and (top_left_x > p1_x) and (bottom_right_x > p1_x)) or ((270 < angle <= 360 or 0 <= angle < 90) and (top_left_x < p1_x) and (bottom_right_x < p1_x)):
            return min_distance, intersection_point, intersection_label
        a, b, c = uf.line_equation_find(p1_x, p1_y, ray_x, ray_y)
        y_inter = lambda x: (-a*x - c) / b if b != 0 else None
        x_inter = lambda y: (-b*y - c) / a if a != 0 else None
        inter_y_where_x_min = y_inter(top_left_x)
        inter_y_where_x_max = y_inter(bottom_right_x)
        inter_x_where_y_min = x_inter(top_left_y)
        inter_x_where_y_max = x_inter(bottom_right_y)
        if inter_y_where_x_min is not None and  top_left_y <= inter_y_where_x_min <= bottom_right_y:
            intersection_y = inter_y_where_x_min
            intersection_x = top_left_x
            distance = uf.euclidean_distance(p1_x, p1_y, intersection_x, intersection_y)
            if distance < min_distance and distance < lidar_range: 
                min_distance = distance
                intersection_point = (intersection_x, intersection_y)
                self.intersection_label = 'obstacle'
        if inter_y_where_x_max is not None and  top_left_y <= inter_y_where_x_max <= bottom_right_y:
            intersection_y = inter_y_where_x_max
            intersection_x = bottom_right_x
            distance = uf.euclidean_distance(p1_x, p1_y, intersection_x, intersection_y)
            if distance < min_distance and distance < lidar_range:
                min_distance = distance
                intersection_point = (intersection_x, intersection_y)
                self.intersection_label = 'obstacle'
        if inter_x_where_y_min is not None and top_left_x <= inter_x_where_y_min <= bottom_right_x:
            intersection_y = top_left_y
            intersection_x = inter_x_where_y_min
            distance = uf.euclidean_distance(p1_x, p1_y, intersection_x, intersection_y)
            if distance < min_distance and distance < lidar_range:
                min_distance = distance
                intersection_point = (intersection_x, intersection_y)
                self.intersection_label = 'obstacle'
        if inter_x_where_y_max is not None and top_left_x <= inter_x_where_y_max <= bottom_right_x:
            intersection_y = bottom_right_y
            intersection_x = inter_x_where_y_max
            distance = uf.euclidean_distance(p1_x, p1_y, intersection_x, intersection_y)
            if distance < min_distance and distance < lidar_range:
                min_distance = distance
                intersection_point = (intersection_x, intersection_y)
                self.intersection_label = 'obstacle'
        return min_distance, intersection_point, self.intersection_label

    def calculate_lidar_measurements(self, state = None, obstacles = None, goal = None, lidar_density = 1, lidar_range = WIDTH*(1/3)):
            self.lidar_range = lidar_range
            self.lidar_density = lidar_density
            self.p1_x = state[0]
            self.p1_y = state[1]
            self.p2_x = state[2]
            self.p2_y = state[3]
            self.goal_x = goal.rect.centerx 
            self.goal_y = goal.rect.centery
            
            # create walls as obstacles
            top_wall = pygame.sprite.Sprite()
            bottom_wall = pygame.sprite.Sprite()
            left_wall = pygame.sprite.Sprite()
            right_wall = pygame.sprite.Sprite()            

            top_wall.rect = pygame.Rect(0, -HEIGHT, WIDTH, HEIGHT)
            bottom_wall.rect = pygame.Rect(0, HEIGHT, WIDTH, HEIGHT)
            left_wall.rect = pygame.Rect(-WIDTH, 0, WIDTH, HEIGHT)
            right_wall.rect = pygame.Rect(WIDTH, 0, WIDTH, HEIGHT)
            
            obstacles.append(top_wall)
            obstacles.append(bottom_wall)
            obstacles.append(left_wall)
            obstacles.append(right_wall)
            
            measurements = {}
            for angle in range(0, 360, self.lidar_density):
                self.min_distance = float('inf')
                self.intersection_point = None
                self.intersection_label = None
                self.angle_rad = math.radians(angle)
                dx = math.cos(self.angle_rad)*self.lidar_range
                dy = math.sin(self.angle_rad)*self.lidar_range
                ray_x = self.p1_x + dx
                ray_y = self.p1_y + dy
                for obstacle in obstacles:
                    self.min_distance, self.intersection_point, self.intersection_label = self.check_if_obstacle_in_path(obstacle, ray_x, ray_y)
                # Check if the ray intersects with the goal or the human
                self.min_distance, self.intersection_point, self.intersection_label = self.check_if_obj_in_path('goal')
                self.min_distance, self.intersection_point, self.intersection_label = self.check_if_obj_in_path('human')
                # If there is no intersection, add a distance of RADIUS
                if self.intersection_point is None:
                    self.min_distance = self.lidar_range
                    self.intersection_label = 'nothing'
                    
                if self.intersection_label == 'nothing':
                    bin_enc = [self.lidar_range,self.lidar_range,self.lidar_range]
                if self.intersection_label == 'obstacle':
                    bin_enc = [self.lidar_range,self.lidar_range,self.min_distance]
                if self.intersection_label == 'human':
                    bin_enc = [self.lidar_range,self.min_distance,self.lidar_range]
                if self.intersection_label == 'goal':
                    bin_enc = [self.min_distance,self.lidar_range,self.lidar_range]
                measurements[angle] = bin_enc 
            # change the dictionary to a list
            measurements = [measurements[key] for key in measurements]
            # delete walls
            obstacles.pop()
            obstacles.pop()
            obstacles.pop()
            obstacles.pop()
            
            return measurements

    def plot_lidar_measurements_on_fig(self, measurements, state = None, obstacles = None, goal = None):
        p1_x = state[0]
        p1_y = state[1]
        p2_x = state[2]
        p2_y = state[3]
        goal_x = goal.rect.centerx
        goal_y = goal.rect.centery
        
        # count the number of obstacles
        n_obs = len(obstacles)
        
        lidar_density = self.lidar_density
        angles_rad = [math.radians(angle) for angle in range(0, 360, lidar_density)]
        
        # plot in plt
        plt.figure()
        # boundaries
        plt.xlim(0, WIDTH)
        plt.ylim(0, HEIGHT)
        for obstacle in obstacles:
            top = obstacle.rect.top
            left = obstacle.rect.left
            width = obstacle.rect.width
            height = obstacle.rect.height
            plt.gca().add_patch(Rectangle((left, top),width, height, color='black'))            
        for i, measurement in enumerate(measurements):
            angle_rad = angles_rad[i]
            dx = math.cos(angle_rad)*measurement[2]
            dy = math.sin(angle_rad)*measurement[2]
            plt.plot([p1_x, p1_x + dx], [p1_y, p1_y + dy], 'yellow')
        plt.scatter(goal_x, goal_y, color='green', label='Goal')
        plt.scatter(p1_x, p1_y, label='Player 1 - Robot', color='red')
        plt.scatter(p2_x, p2_y, label='Player 2 - Human', color='blue')
        plt.gca().invert_yaxis()  # Invert y-axis to match the new orientation

        time_ = pygame.time.get_ticks()
        # save 
        plt.savefig('.\lidar\lidar_measurements ' + str(time_) + '.png')
        
    def plot_lidar_measurements_on_screen(self, measurements, state = None, obstacles = None, goal = None):
        p1_x = state[0]
        p1_y = state[1]
        p2_x = state[2]
        p2_y = state[3]
        goal_x = goal.rect.centerx
        goal_y = goal.rect.centery
        
        # BUT DONT SHOW THE SCREEN         
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        screen.fill(WHITE)
        pygame.draw.circle(screen, RED, (p1_x, p1_y), PLAYER_SIZE)
        pygame.draw.circle(screen, BLUE, (p2_x, p2_y), PLAYER_SIZE)
        pygame.draw.circle(screen, GREEN, (goal_x, goal_y), PLAYER_SIZE)
        
        # draw obstacles 
        for obstacle in obstacles:
            pygame.draw.rect(screen, BLACK, obstacle.rect)
            
        for i, measurement in enumerate(measurements):
            angle_rad = math.radians(i)
            dx = math.cos(angle_rad)*measurement[2]
            dy = math.sin(angle_rad)*measurement[2]
            pygame.draw.line(screen, RED, (self.p1_x, self.p1_y), (self.p1_x + dx, self.p1_y + dy), 1)
            pygame.display.update()
        pygame.draw.circle(screen, RED, (p1_x, p1_y), PLAYER_SIZE)
        pygame.draw.circle(screen, BLUE, (p2_x, p2_y), PLAYER_SIZE)
        pygame.draw.circle(screen, GREEN, (goal_x, goal_y), PLAYER_SIZE)
        # save the plot with time
        time_ = pygame.time.get_ticks()
        pygame.image.save(screen, '.\lidar\lidar_measurements ' + str(time_) + '.png')

           

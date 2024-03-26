import pandas as pd
import os
import sys
# one folder up
sys.path.insert(1, './')
import useful_functions as uf
import math
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool

WIDTH = 800
HEIGHT = 600
RADIUS = 1/3*WIDTH

# Loop over all the CSV files in the directory
data_input_path = '/data/processed_data/game_and_map_data'
data_output_path = '/data/processed_data/game_and_map_data_lidar_like_with_walls'
data_output_directory = data_output_path.split('/')[-1]
if data_output_directory not in os.listdir('./data/processed_data/'):
    os.mkdir("." + data_output_path)

def process_fun(filename): 
        filename = filename.split('.')[0]
        # Load the data
        data = pd.read_csv("." + data_input_path + "/" + filename + ".csv")

        # Identify obstacle columns dynamically
        obstacle_cols = [col for col in data.columns if col.startswith('obs_')]
        obstacle_nums = [int(col.split('_')[1]) for col in obstacle_cols]
        obstacle_nums = list(set(obstacle_nums))

        measurements_df = pd.DataFrame()
        # Apply the function to each row
        measurements_df = data.apply(lidar_measurements, axis=1)
        measurements_df = pd.DataFrame(measurements_df.tolist())

        # Add actions, reward and timestamp column
        measurements_df['P1_action'] = data['P1_Direction']
        measurements_df['P2_action'] = data['P2_Direction']
        measurements_df['reward'] = data['Total_Score']
        measurements_df['timestamp_milliseconds'] = data['Elapsed_time_miliseconds']

        columns_titles = []
        columns_titles.extend(['P1_lidar_meas_in_' + str(i) + '_deg' for i in range(360)])
        columns_titles.extend(['P1_action', 'P2_action', 'reward', 'timestamp_milliseconds'])

        measurements_df.columns = columns_titles

        # Save the result to a new CSV file
        measurements_df.to_csv("." + data_output_path + "/" + filename + "_lidar_like_data.csv", index=False)
        print("Saved " + filename + "_lidar_like_data.csv")
    
def line_equation_find(x1, y1, x2, y2):
    # Calculate the coefficients
    a = y1 - y2
    b = x2 - x1
    c = x1 * y2 - x2 * y1
    return a, b, c

def lidar_measurements(row):
    obstacle_nums = [int(col.split('_')[1]) for col in row.keys() if col.startswith('obs_')]
    obstacle_nums = list(set(obstacle_nums))
    p1_x = row['P1_X']
    p1_y = row['P1_Y']
    p2_x = row['P2_X']
    p2_y = row['P2_Y']
    goal_x = row['goal_x']
    goal_y = row['goal_y']
    measurements = {}
    # add 4 walls: 
    obstacle_nums.append('top_wall')
    obstacle_nums.append('bottom_wall')
    obstacle_nums.append('left_wall')
    obstacle_nums.append('right_wall')
    for angle in range(0, 360, 1):
        min_distance = float('inf')
        intersection_point = None
        intersection_label = None
        rad_angle = math.radians(angle)
        dx = math.cos(rad_angle)*RADIUS
        dy = math.sin(rad_angle)*RADIUS
        ray_x = p1_x + dx
        ray_y = p1_y + dy
        for obstacle_num in obstacle_nums:
            if obstacle_num == 'top_wall':
                top_left_x = 0
                top_left_y = -HEIGHT + 0
                height = HEIGHT + 0
                width = WIDTH + 0
                bottom_right_x = top_left_x + width
                bottom_right_y = top_left_y + height
            elif obstacle_num == 'bottom_wall':
                top_left_x = 0
                top_left_y = HEIGHT + 0
                height = HEIGHT + 0
                width = WIDTH + 0
                bottom_right_x = top_left_x + width
                bottom_right_y = top_left_y + height
            elif obstacle_num == 'left_wall':
                top_left_x = -WIDTH + 0
                top_left_y = 0
                height = HEIGHT + 0
                width = WIDTH + 0
                bottom_right_x = top_left_x + width
                bottom_right_y = top_left_y + height
            elif obstacle_num == 'right_wall':
                top_left_x = WIDTH + 0
                top_left_y = 0
                height = HEIGHT + 0
                width = WIDTH + 0
                bottom_right_x = top_left_x + width
                bottom_right_y = top_left_y + height
            else:
                top_left_x = row['obs_' + str(obstacle_num) + '_x']
                top_left_y = row['obs_' + str(obstacle_num) + '_y']
                height = row['obs_' + str(obstacle_num) + '_height']
                width = row['obs_' + str(obstacle_num) + '_width']
                bottom_right_x = top_left_x + width
                bottom_right_y = top_left_y + height
            # if the obstacle is not in the ray's direction continue
            if ((0 < angle < 180) and (top_left_y < p1_y) and (bottom_right_y < p1_y)) or ((180 < angle < 360) and (top_left_y > p1_y) and (bottom_right_y > p1_y)):
                continue
            if ((90 < angle < 270) and (top_left_x > p1_x) and (bottom_right_x > p1_x)) or ((270 < angle < 360 or 0 < angle < 90) and (top_left_x < p1_x) and (bottom_right_x < p1_x)):
                continue              
            a, b, c = line_equation_find(p1_x, p1_y, ray_x, ray_y)
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
                if distance < min_distance and distance < RADIUS: 
                    min_distance = distance
                    intersection_point = (intersection_x, intersection_y)
                    intersection_label = 'obstacle'
            if inter_y_where_x_max is not None and  top_left_y <= inter_y_where_x_max <= bottom_right_y:
                intersection_y = inter_y_where_x_max
                intersection_x = bottom_right_x
                distance = uf.euclidean_distance(p1_x, p1_y, intersection_x, intersection_y)
                if distance < min_distance and distance < RADIUS:
                    min_distance = distance
                    intersection_point = (intersection_x, intersection_y)
                    intersection_label = 'obstacle'
            if inter_x_where_y_min is not None and top_left_x <= inter_x_where_y_min <= bottom_right_x:
                intersection_y = top_left_y
                intersection_x = inter_x_where_y_min
                distance = uf.euclidean_distance(p1_x, p1_y, intersection_x, intersection_y)
                if distance < min_distance and distance < RADIUS:
                    min_distance = distance
                    intersection_point = (intersection_x, intersection_y)
                    intersection_label = 'obstacle'
            if inter_x_where_y_max is not None and top_left_x <= inter_x_where_y_max <= bottom_right_x:
                intersection_y = bottom_right_y
                intersection_x = inter_x_where_y_max
                distance = uf.euclidean_distance(p1_x, p1_y, intersection_x, intersection_y)
                if distance < min_distance and distance < RADIUS:
                    min_distance = distance
                    intersection_point = (intersection_x, intersection_y)
                    intersection_label = 'obstacle'
        # Check if the ray intersects with the goal
        angle_to_goal = math.atan2(goal_y - p1_y, goal_x - p1_x)
        if angle_to_goal < 0:
            angle_to_goal += 2 * math.pi
        if abs(angle_to_goal - rad_angle) < math.radians(1):
            distance = uf.euclidean_distance(p1_x, p1_y, goal_x, goal_y)
            if distance < min_distance and distance < RADIUS:
                min_distance = distance
                intersection_point = (goal_x, goal_y)
                intersection_label = 'goal'
        angle_to_human = math.atan2(p2_y - p1_y, p2_x - p1_x)
        if angle_to_human < 0:
            angle_to_human += 2 * math.pi
        if abs(angle_to_human - rad_angle) < math.radians(1):
            distance = uf.euclidean_distance(p1_x, p1_y, p2_x, p2_y)
            if distance < min_distance and distance < RADIUS:
                min_distance = distance
                intersection_point = (p2_x, p2_y)
                intersection_label = 'human'
        # If there is no intersection, add a distance of 50
        if intersection_point is None:
            min_distance = RADIUS
            intersection_label = 'nothing'
        measurements[angle] = [min_distance, intersection_label, intersection_point] # intersection_point for debugging
        # print(f"Angle: {angle}, Distance: {min_distance}, Label: {intersection_label}, Intersection Point: {intersection_point}")
    # Plot the p1_x, p1_y and the measurements
    # plt.figure(figsize=(WIDTH/100, HEIGHT/100))
    # plt.scatter(p1_x, p1_y, color='red', label='Robot')
    # plt.scatter(p2_x, p2_y, color='blue', label='Human')
    # plt.scatter(goal_x, goal_y, color='green', label='Goal')
    # for obstacle_num in obstacle_nums:
    #     if obstacle_num != 'top_wall' and obstacle_num != 'bottom_wall' and obstacle_num != 'left_wall' and obstacle_num != 'right_wall':
    #         top_left_x = row['obs_' + str(obstacle_num) + '_x']
    #         top_left_y = row['obs_' + str(obstacle_num) + '_y']
    #         height = row['obs_' + str(obstacle_num) + '_height']
    #         width = row['obs_' + str(obstacle_num) + '_width']
    #         plt.gca().add_patch(plt.Rectangle((top_left_x, top_left_y), width, height, color='black'))
    # for angle in range(0, 360, 1):
    #     intersection_point = measurements[angle][2]
    #     if intersection_point:
    #         plt.plot([p1_x, intersection_point[0]], [p1_y, intersection_point[1]], color='red')
        # draw the lidar rays 
        # plt.plot([p1_x, p1_x + math.cos(math.radians(angle)) * RADIUS], [p1_y, p1_y + math.sin(math.radians(angle)) * RADIUS], color='pink')
    # plt.xlim(0, WIDTH)
    # plt.ylim(0, HEIGHT)
    # plt.show()
    return measurements
    

        
# use multiprocessing to parallelize the process

# Representation of the data lidar-like sensor
# distance, human, goal, obstacle, nothing = [50, 0, 0, 1, 0]
# The distance to the obstacle is 50, there is no human, no goal, there is an obstacle, and there is nothing else in this direction


if __name__ == '__main__':   
    filenames = os.listdir("." + data_input_path)
    pool = Pool()
    result = pool.map(process_fun, filenames)
    pool.close()    
    pool.join()
    print(result)

    
    

        
        
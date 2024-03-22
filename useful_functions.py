import numpy as np
import pandas as pd

def closest_point_on_rectangle(top_left, top_right, bottom_left, bottom_right, point):
    # Define vectors representing edges of the rectangle
    edges = [(top_left, top_right), (top_right, bottom_right),
             (bottom_right, bottom_left), (bottom_left, top_left)]

    # Initialize variables for storing closest distance and point
    closest_distance = float('inf')
    closest_point = None

    # Iterate through each edge of the rectangle
    for edge_start, edge_end in edges:
        # Calculate vector from edge start to point
        v = (point[0] - edge_start[0], point[1] - edge_start[1])

        # Calculate edge vector
        edge_vector = (edge_end[0] - edge_start[0], edge_end[1] - edge_start[1])

        # Calculate dot product
        dot_product = v[0] * edge_vector[0] + v[1] * edge_vector[1]

        # Calculate squared length of edge
        edge_length_squared = edge_vector[0] ** 2 + edge_vector[1] ** 2

        # Calculate projection parameter
        t = max(0, min(1, dot_product / edge_length_squared))

        # Calculate projected point on edge
        projected_point = (edge_start[0] + t * edge_vector[0], edge_start[1] + t * edge_vector[1])

        # Calculate distance between original point and projected point
        distance = ((point[0] - projected_point[0]) ** 2 + (point[1] - projected_point[1]) ** 2) ** 0.5

        # Update closest point if necessary
        if distance < closest_distance:
            closest_distance = distance
            closest_point = projected_point

    return closest_point

def calculate_corners(x, y, width, height):
    top_left = (x, y)
    top_right = (x + width, y)
    bottom_left = (x, y + height)
    bottom_right = (x + width, y + height)
    return top_left, top_right, bottom_left, bottom_right

def euclidean_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def distance_to_obstacle(player_x, player_y, obstacle_x, obstacle_y, width, height):
    top_left, top_right, bottom_left, bottom_right = calculate_corners(obstacle_x, obstacle_y, width, height)
    # find the closest point on the rectangular obstacle to the player
    closest_x, closest_y = closest_point_on_rectangle(top_left, top_right, bottom_left, bottom_right, (player_x, player_y))

def closest_point_on_rectangle(top_left, top_right, bottom_left, bottom_right, point):
    # Define vectors representing edges of the rectangle
    edges = [(top_left, top_right), (top_right, bottom_right),
             (bottom_right, bottom_left), (bottom_left, top_left)]

    # Initialize variables for storing closest distance and point
    closest_distance = float('inf')
    closest_point = None

    # Iterate through each edge of the rectangle
    for edge_start, edge_end in edges:
        # Calculate vector from edge start to point
        v = (point[0] - edge_start[0], point[1] - edge_start[1])

        # Calculate edge vector
        edge_vector = (edge_end[0] - edge_start[0], edge_end[1] - edge_start[1])

        # Calculate dot product
        dot_product = v[0] * edge_vector[0] + v[1] * edge_vector[1]

        # Calculate squared length of edge
        edge_length_squared = edge_vector[0] ** 2 + edge_vector[1] ** 2

        # Calculate projection parameter
        t = max(0, min(1, dot_product / edge_length_squared))

        # Calculate projected point on edge
        projected_point = (edge_start[0] + t * edge_vector[0], edge_start[1] + t * edge_vector[1])

        # Calculate distance between original point and projected point
        distance = ((point[0] - projected_point[0]) ** 2 + (point[1] - projected_point[1]) ** 2) ** 0.5

        # Update closest point if necessary
        if distance < closest_distance:
            closest_distance = distance
            closest_point = projected_point

    return closest_point

def calculate_corners(x, y, width, height):
    top_left = (x, y)
    top_right = (x + width, y)
    bottom_left = (x, y + height)
    bottom_right = (x + width, y + height)
    return top_left, top_right, bottom_left, bottom_right

def euclidean_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def distance_to_obstacle(player_x, player_y, obstacle_x, obstacle_y, width, height):
    top_left, top_right, bottom_left, bottom_right = calculate_corners(obstacle_x, obstacle_y, width, height)
    # find the closest point on the rectangular obstacle to the player
    closest_x, closest_y = closest_point_on_rectangle(top_left, top_right, bottom_left, bottom_right, (player_x, player_y))
    return euclidean_distance(player_x, player_y, closest_x, closest_y)

def points_in_radius_on_rectangular(top_left, top_right, bottom_left, bottom_right, center, radius):
    points = []
    # find the center of the rectangle
    rectangle_center = ((top_left[0] + top_right[0]) / 2, (top_left[1] + bottom_left[1]) / 2)
    # find the distance between the center of the rectangle and the center of the circle
    distance = euclidean_distance(rectangle_center[0], rectangle_center[1], center[0], center[1])
    # if the distance is greater than the radius of the circle + the diagonal of the rectangle
    # then the circle is outside the rectangle
    if distance > radius + np.sqrt((top_right[0] - top_left[0]) ** 2 + (top_right[1] - top_left[1]) ** 2):
        return points
    # if the distance is less than the radius of the circle - the diagonal of the rectangle
    # then the circle is inside the rectangle, return all points of the rectangle perimeter
    if distance < radius - np.sqrt((top_right[0] - top_left[0]) ** 2 + (top_right[1] - top_left[1]) ** 2):
        for x in range(int(top_left[0]), int(top_right[0])):
            points.append((x, int(top_left[1])))
            points.append((x, int(bottom_left[1])))
        for y in range(int(top_left[1]), int(bottom_left[1])):
            points.append((int(top_left[0]), y))
            points.append((int(top_right[0]), y))
        return points
    # if the circle is intersecting the rectangle
    # find the points on the rectangle perimeter only that are inside the circle 
    # and add them to the list of points
    for x in range(int(top_left[0]), int(top_right[0])):
        if euclidean_distance(center[0], center[1], x, top_left[1]) <= radius:
            points.append((x, top_left[1]))

    # Iterate over the right side of the rectangle
    for y in range(int(top_right[1]), int(bottom_left[1])):
        if euclidean_distance(center[0], center[1], top_right[0], y) <= radius:
            points.append((top_right[0], y))

    # Iterate over the bottom side of the rectangle
    for x in range(int(bottom_left[0]), int(top_left[0]), -1):
        if euclidean_distance(center[0], center[1], x, bottom_left[1]) <= radius:
            points.append((x, bottom_left[1]))

    # Iterate over the left side of the rectangle
    for y in range(int(bottom_left[1]), int(top_left[1]), -1):
        if euclidean_distance(center[0], center[1], bottom_left[0], y) <= radius:
            points.append((bottom_left[0], y))
    return points 
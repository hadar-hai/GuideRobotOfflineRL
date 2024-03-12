# Data Storage classes for the initial map data and online player data
import csv
import os
import datetime

class MapData:
    def __init__(self, obstacles, goal_x, goal_y, directory=None):
        if directory is None:
            directory = os.getcwd()
        self.directory = directory
        self.filename = self.generate_filename()
        self.filepath = os.path.join(self.directory, self.filename)
        self.obstacles = obstacles
        self.goal_x = goal_x
        self.goal_y = goal_y

        # Ensure the directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Initialize the file with headers
        with open(self.filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            headers = ['goal_x', 'goal_y']
            for obstacle_id in range(len(obstacles)):
                headers.extend([
                    f"obs_{obstacle_id}_x",
                    f"obs_{obstacle_id}_y",
                    f"obs_{obstacle_id}_width",
                    f"obs_{obstacle_id}_height"
                ])
            writer.writerow(headers)

    def generate_filename(self):
        # Count the number of existing files to determine the next file name
        existing_files = [f for f in os.listdir(self.directory) if f.startswith("map_data_") and f.endswith(".csv")]
        next_file_number = len(existing_files)
        filename = f"map_data_{next_file_number:02d}.csv"
        return filename

    def update_map_data(self):
        map_data = [self.goal_x, self.goal_y]
        for obstacle in self.obstacles:
            obstacle_data = [obstacle.x, obstacle.y, obstacle.width, obstacle.height]
            map_data.extend(obstacle_data)
        # Append the parameters
        with open(self.filepath, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(map_data)

    def get_filepath(self):
        return self.filepath

class GameData:
    def __init__(self, directory=os.getcwd()):
            self.directory = directory
            self.filename = self.generate_filename()
            self.filepath = os.path.join(self.directory, self.filename)

            # Ensure the directory exists
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)

            # Initialize the file with headers
            with open(self.filepath, 'w', newline='') as file:
                writer = csv.writer(file)
                headers = ['P1_X', 'P1_Y', 'P1_Direction', 'P1_Crashed', 'P1_ReachedGoal', 'P1_Score',
                           'P2_X', 'P2_Y', 'P2_Direction', 'P2_Crashed', 'P2_ReachedGoal', 'P2_Score']
                writer.writerow(headers)

    def generate_filename(self):
        # Count the number of existing files to determine the next file name
        existing_files = [f for f in os.listdir(self.directory) if f.startswith("game_data_") and f.endswith(".csv")]
        next_file_number = len(existing_files)
        filename = f"game_data_{next_file_number:02d}.csv"
        return filename

    def update_state_vector(self, player1_state, player2_state, player1_score, player2_score):
        combined_state = player1_state + [player1_score] + player2_state + [player2_score]
        # Append the new state directly to the file
        with open(self.filepath, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(combined_state)

    def get_filepath(self):
        return self.filepath


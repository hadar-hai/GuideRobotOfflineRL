import csv
import ast  # For literal evaluation of lists

def transform_csv(input_file, output_file):
    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)  # Read the header

        # Count the number of obstacles
        num_obstacles = sum(1 for column in header if column.startswith('obs_')) // 4

        # Generate the titles line
        new_header_order = ['goal_x', 'goal_y'] + [f"obs_{i}_{suffix}" for i in range(num_obstacles) for suffix in ['x', 'y', 'width', 'height']]

        with open(output_file, 'w', newline='') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(new_header_order)  # Write the reordered header

            # Read and process the data
            data = next(reader)
            new_data = [data[0], data[1]]  # Goal_x and Goal_y remains unchanged

            # Transform observation data
            for i in range(2, len(data)):
                obs_data = ast.literal_eval(data[i])  # Evaluate the list as Python list
                new_data.append(obs_data[0])
                new_data.append(obs_data[1])
                new_data.append(obs_data[3])
                new_data.append(obs_data[2])

            writer.writerow(new_data)  # Write the transformed data


# Usage
input_file = './data/2024_02_21/dataset1/map_data_00.csv'
output_file = './data/2024_02_21/dataset1/map_data_00_.csv'
transform_csv(input_file, output_file)

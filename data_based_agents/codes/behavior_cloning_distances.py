import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Get the current directory
current_dir = os.path.dirname(__file__)

# Navigate two levels up
two_folders_before = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Load labels from CSV file
data_dir = os.path.join(two_folders_before, 'data', 'processed_data', 'game_and_map_data_distances_in_radius_not_moving_actions_removed')

# Read all csv data files in the directory
data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
data = pd.concat([pd.read_csv(os.path.join(data_dir, f)) for f in data_files])

# Extract features and labels
# Drop the P1_action, P2_action, reward, and timestamp_milliseconds columns   (P1_action is the label)
X = data.drop(['P1_action', 'P2_action', 'reward', 'timestamp_milliseconds'], axis=1)
y = data['P1_action']

# Model folder
model_dir = os.path.join(two_folders_before, 'data_based_agents','models')

# Display shapes of X and y
print("Shape of X:", X.shape)
print("Shape of y:", y.shape)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Split data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.125, random_state=42)

# Standardize the data according to the training set
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

# Define neural network architecture
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(4, activation='softmax')  # 4 classes for P1 actions without not moving action
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model and save the history and set learning rate
model.optimizer.lr = 0.01
history = model.fit(X_train, y_train, epochs=500, batch_size=128, validation_data=(X_val, y_val))

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f'Test Accuracy: {accuracy}')

# Make predictions
predictions = model.predict(X_test)

# Save in csv
history_df = pd.DataFrame(history.history)
history_df.to_csv(model_dir + "\\behavior_cloning_distances_not_moving_actions_removed.csv")

y_pred = np.argmax(predictions, axis=1)
confusion_matrix = tf.math.confusion_matrix(y_test, y_pred)
print(confusion_matrix)

# save test accuracy and confusion matrix in text file
with open(model_dir + "\\behavior_cloning_distances_not_moving_actions_removed.txt", "w") as f:
    f.write("Test accuracy: " + str(accuracy) + "\n")
    f.write("Confusion matrix: \n")
    f.write(str(confusion_matrix)) 


# Save the model
model.save(model_dir + "\\behavior_cloning_distances_not_moving_actions_removed.h5")
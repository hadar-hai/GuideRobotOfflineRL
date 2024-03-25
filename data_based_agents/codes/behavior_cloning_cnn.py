import tensorflow as tf
from tensorflow.keras import layers, models
import os
import cv2
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import os

# Define the CNN model
def create_model(input_shape):
    model = models.Sequential()
    
    # Convolutional layers
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    
    # Dense layers
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(5, activation='softmax'))  # 5 output classes
    
    # Compile the model
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model

# Create the model
input_shape = (100, 100, 3)
model = create_model(input_shape)
model.summary()
# Get the current directory
current_dir = os.path.dirname(__file__)

# Navigate two levels up
two_folders_before = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Load labels from CSV file
labels_dir = os.path.join(two_folders_before, 'data', 'processed_data', 'processed_data_images')
labels_filename = "labels.csv"
labels_df = pd.read_csv(os.path.join(labels_dir, labels_filename))

# Load images
image_dir = os.path.join(two_folders_before, 'data', 'processed_data', 'processed_data_images')
# Get list of image paths without labels.csv
image_paths = [os.path.join(image_dir, filename) for filename in os.listdir(image_dir) if filename != labels_filename]
images = []
labels = []

# Model folder
model_dir = os.path.join(two_folders_before, 'data_based_agents','models')

# Iterate through image paths
for image_path in image_paths:
    # Read image as RGB
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (100, 100))
    # show the first image 
    # plt.imshow(image)
    # plt.axis('off')  # Hide axes
    # plt.show()
        
    images.append(image)
    
    # Get label
    # Extract filename from path
    filename = os.path.basename(image_path).split('.')[0]
    label_row = labels_df.loc[labels_df['dataset_game_frame'] == filename]
    label = label_row['label'].values[0]
    labels.append(label)
    if len(labels) % 100 == 0:
        print("Read image", filename, "with label", label)

# Convert lists to numpy arrays
X = np.array(images)
y = np.array(labels)

# Reshape X to match model input shape
X = X.reshape(-1, 100, 100, 3)

# Normalize pixel values to be between 0 and 1
X = X.astype('float32') / 255.0

# Display shapes of X and y
print("Shape of X:", X.shape)
print("Shape of y:", y.shape)

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.125)

# Standardize the data
x_train_shape = X_train.shape
x_val_shape = X_val.shape
x_test_shape = X_test.shape

# Reshape the data to 2D arrays for applying StandardScaler
X_train_flat = X_train.reshape(x_train_shape[0], -1)
X_val_flat = X_val.reshape(x_val_shape[0], -1)
X_test_flat = X_test.reshape(x_test_shape[0], -1)

# Initialize StandardScaler and fit it to the training data
x_scaler = StandardScaler().fit(X_train_flat)

# Transform the training, validation, and test data using the scaler
X_train_scaled = x_scaler.transform(X_train_flat)
X_val_scaled = x_scaler.transform(X_val_flat)
X_test_scaled = x_scaler.transform(X_test_flat)

# Reshape the scaled data back to the original shape
X_train_scaled = X_train_scaled.reshape(x_train_shape)
X_val_scaled = X_val_scaled.reshape(x_val_shape)
X_test_scaled = X_test_scaled.reshape(x_test_shape)

# Store training and validation loss and accuracy in csv file
# Train the model
history = model.fit(X_train_scaled, y_train, epochs=50, batch_size=32, validation_data=(X_val_scaled, y_val))

# Plot training and validation loss
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='validation')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Save in csv
history_df = pd.DataFrame(history.history)
history_df.to_csv(model_dir + "\\behavior_cloning_cnn_100.csv")

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test_scaled, y_test, verbose=2)
print('\nTest accuracy:', test_acc)

# confusion matrix
y_pred = model.predict(X_test_scaled)
y_pred = np.argmax(y_pred, axis=1)
confusion_matrix = tf.math.confusion_matrix(y_test, y_pred)
print(confusion_matrix)

# save test accuracy and confusion matrix in text file
with open(model_dir + "\\behavior_cloning_cnn_100.txt", "w") as f:
    f.write("Test accuracy: " + str(test_acc) + "\n")
    f.write("Confusion matrix: \n")
    f.write(str(confusion_matrix)) 


# Save the model
model.save(model_dir + "\\behavior_cloning_cnn_100.h5")
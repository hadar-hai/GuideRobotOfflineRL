import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

# Set random seed for reproducibility
torch.manual_seed(0)
np.random.seed(0)

# Define file paths
features_path = r".\data\processed_data\lidar_3beam_data_new_r_with_filenames.csv"
labels_path = r".\data\processed_data\game_and_map_data_lidar_like_with_walls_arranged\labels.csv"
scaler_path = r".\data_based_agents\models\scalers\scaler_pytorch_without_not_moving.pkl"

# Load data
features = pd.read_csv(features_path).drop(columns=['final_row_flag', 'file_name'])
labels = pd.read_csv(labels_path).drop(columns=['file_name'])

# remove the not moving class from the data
features = features[labels['P1_action'] != 4]
labels = labels[labels['P1_action'] != 4]

# Convert to PyTorch tensors
x_tensor = torch.tensor(features.values, dtype=torch.float32)
y_tensor = torch.tensor(labels.values.flatten(), dtype=torch.long)

# Split data into train, validation, and test sets
indices = np.random.permutation(len(x_tensor))
train_indices, val_indices, test_indices = np.split(indices, [int(0.8 * len(indices)), int(0.9 * len(indices))])

# Normalize the features based on the train set
scaler = MinMaxScaler()
x_train_normalized = scaler.fit_transform(x_tensor[train_indices])
# print the max value of the normalized data
print(np.max(x_train_normalized))
# print the min value of the normalized data
print(np.min(x_train_normalized))

x_tensor[train_indices] = torch.tensor(x_train_normalized, dtype=torch.float32)
x_tensor[val_indices] = torch.tensor(scaler.transform(x_tensor[val_indices]), dtype=torch.float32)
x_tensor[test_indices] = torch.tensor(scaler.transform(x_tensor[test_indices]), dtype=torch.float32)

# Create DataLoader for each set
def create_data_loader(indices, batch_size=128):
    dataset = TensorDataset(x_tensor[indices], y_tensor[indices])
    return DataLoader(dataset, batch_size=batch_size)

train_loader = create_data_loader(train_indices)
val_loader = create_data_loader(val_indices)
test_loader = create_data_loader(test_indices)

# Define the model
class LidarLikeNet(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(LidarLikeNet, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.Dropout(0.2),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Linear(16, output_dim)
        )

    def forward(self, x):
        return self.layers(x)

# Initialize the model, criterion, and optimizer
model = LidarLikeNet(x_tensor.shape[1], 5)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training the model
num_epochs = 200
train_losses, val_losses, val_accuracies = [], [], []
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

for epoch in range(num_epochs):
    model.train()
    train_loss = 0
    for x_batch, y_batch in train_loader:
        x_batch, y_batch = x_batch.to(device), y_batch.to(device)
        optimizer.zero_grad()
        y_pred = model(x_batch)
        loss = criterion(y_pred, y_batch)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    train_losses.append(train_loss / len(train_loader))

    model.eval()
    val_loss, val_accuracy = 0, 0
    with torch.no_grad():
        for x_val_batch, y_val_batch in val_loader:
            x_val_batch, y_val_batch = x_val_batch.to(device), y_val_batch.to(device)
            y_val_pred = model(x_val_batch)
            val_loss += criterion(y_val_pred, y_val_batch).item()
            val_accuracy += (y_val_pred.argmax(1) == y_val_batch).float().mean().item()
    val_losses.append(val_loss / len(val_loader))
    val_accuracies.append(val_accuracy / len(val_loader))

    print(f'Epoch {epoch + 1}/{num_epochs}, Train Loss: {train_losses[-1]:.4f}, Val Loss: {val_losses[-1]:.4f}, Val Accuracy: {val_accuracies[-1]:.4f}')


# save the plots as png 
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Val Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.savefig(r".\data_based_agents\plots\train_val_loss_lidar_pytorch_without_not_moving.png")
plt.close()

plt.plot(val_accuracies, label='Val Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.savefig(r".\data_based_agents\plots\val_accuracy_lidar_pytorch_without_not_moving.png")


# Evaluate the model
model.eval()
y_true, y_pred = [], []
with torch.no_grad():
    for x_batch, y_batch in test_loader:
        x_batch, y_batch = x_batch.to(device), y_batch.to(device)
        y_test_pred = model(x_batch)
        y_true.extend(y_batch.cpu().numpy())
        y_pred.extend(y_test_pred.argmax(1).cpu().numpy())

# Calculate and print the test accuracy
accuracy = np.mean(np.array(y_true) == np.array(y_pred))
print(f'Test Accuracy: {accuracy:.4f}')

# Calculate the confusion matrix
conf_matrix = confusion_matrix(y_true, y_pred)
# Save the confusion matrix as a plot
plt.figure(figsize=(10, 7))
sns.heatmap(conf_matrix, annot=True, fmt='d')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.savefig(r".\data_based_agents\plots\confusion_matrix_lidar_pytorch_without_not_moving.png")

# Save the scaler
joblib.dump(scaler, scaler_path)

#save the model 
torch.save(model.state_dict(), r".\data_based_agents\models\behavior_cloning_lidar_pytorch_without_not_moving.pth")

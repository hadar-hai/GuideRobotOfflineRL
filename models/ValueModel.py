import torch.nn as nn
import torch.nn.functional as F

class ValueModel(nn.Module):
    def __init__(self, input_dim):
        super(ValueModel, self).__init__()
        # Define the layers
        self.fc1 = nn.Linear(input_dim, 128)  # First layer taking the input dimension to 128 units
        self.fc2 = nn.Linear(128, 64)         # Second layer: 128 to 64 units
        self.fc3 = nn.Linear(64, 32)          # Corrected third layer: 64 to 32 units
        self.fc4 = nn.Linear(32, 1)           # Final layer: 32 units to 1 output

    def forward(self, x):
        # Define the forward pass using ReLU activations for hidden layers
        x = F.relu(self.fc1(x))  # Activation for first layer
        x = F.relu(self.fc2(x))  # Activation for second layer
        x = F.relu(self.fc3(x))  # Activation for third layer
        x = self.fc4(x)          # No activation for the final layer, assuming a regression task
        return x

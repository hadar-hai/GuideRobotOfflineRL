import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


import torch.nn as nn
import torch.nn.functional as F

class BCAgent(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(BCAgent, self).__init__()
        # Use the input_dim and output_dim arguments to adjust layer dimensions
        self.fc1 = nn.Linear(input_dim, 1024)
        self.bn1 = nn.BatchNorm1d(1024)
        self.dp1 = nn.Dropout(0.2)

        self.fc2 = nn.Linear(1024, 512)
        self.bn2 = nn.BatchNorm1d(512)
        self.dp2 = nn.Dropout(0.2)

        self.fc3 = nn.Linear(512, 128)
        self.bn3 = nn.BatchNorm1d(128)
        self.dp3 = nn.Dropout(0.2)

        self.fc4 = nn.Linear(128, 64)
        self.bn4 = nn.BatchNorm1d(64)
        self.dp4 = nn.Dropout(0.2)

        self.fc5 = nn.Linear(64, 32)
        self.bn5 = nn.BatchNorm1d(32)
        self.dp5 = nn.Dropout(0.2)

        self.fc6 = nn.Linear(32, output_dim)  # Use output_dim for the output layer

    def forward(self, x):
        x = F.relu(self.dp1(self.bn1(self.fc1(x))))
        x = F.relu(self.dp2(self.bn2(self.fc2(x))))
        x = F.relu(self.dp3(self.bn3(self.fc3(x))))
        x = F.relu(self.dp4(self.bn4(self.fc4(x))))
        x = F.relu(self.dp5(self.bn5(self.fc5(x))))
        x = self.fc6(x)
        return x
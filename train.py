import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn

# -- Define dataset --

class HandDataset(Dataset): # subclass Dataset
    def __init__(self, csv_file):
        data = pd.read_csv(csv_file, header=None)

        self.X = torch.tensor(data.iloc[:, :-1].values, dtype=torch.float32) # first 63 cols of csv have coords
        self.y = torch.tensor(data.iloc[:, -1].values, dtype=torch.long) # last col has actual labels # note: loss fn needs ints

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    
# -- Build NN --

class HandNet(nn.Module): # subclass nn.Module
    def __init__(self, num_classes):
        super().__init__() # inherit all of nn.Module __init__
        # Layers
        self.net = nn.Sequential(
            nn.Linear(63, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.net(x) # pass through layers

# -- Training Loop --

dataset = HandDataset("RH_dataset.csv") # try with right hand data for now
loader = DataLoader(dataset, batch_size=64, shuffle=True)

model = HandNet(num_classes=7)

criterion = nn.CrossEntropyLoss() # loss fn
optimizer = torch.optim.Adam(model.parameters(), lr=0.001) # weight correction (Adaptive Moment Estimation)

for epoch in range(30):
    total_loss = 0

    for X, y in loader:
        pred = model(X)
        loss = criterion(pred, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch}: {total_loss:.4f}")

torch.save(model.state_dict(), "RH_only_model.pt")
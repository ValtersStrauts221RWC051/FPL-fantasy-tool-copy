import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


FEATURES = [
    "element",
    "round",
    "minutes",
    "assists",
    "clean_sheets",
    "goals_conceded",
    "own_goals",
    "penalties_saved",
    "penalties_missed",
    "yellow_cards",
    "red_cards",
    "saves",
    "bonus",
    "bps",
    "influence",
    "creativity",
    "threat",
    "defensive_contribution",
    "expected_assists",
    "expected_goal_involvements",
    "expected_goals_conceded",
    "form_last_6_gw"
]

TARGET = "total_points"
EPOCHS = 4000
LR = 1e-4
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class PlayerDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class PlayerRegressor(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.25),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.net(x)

def train_epoch(model, loader, optimizer, criterion):
    model.train()
    total_loss = 0.0

    for X, y in loader:
        X, y = X.to(DEVICE), y.to(DEVICE)

        optimizer.zero_grad()
        preds = model(X)
        loss = criterion(preds, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(X)

    return total_loss / len(loader.dataset)


def eval_epoch(model, loader, criterion):
    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for X, y in loader:
            X, y = X.to(DEVICE), y.to(DEVICE)
            preds = model(X)
            loss = criterion(preds, y)
            total_loss += loss.item() * len(X)

    return total_loss / len(loader.dataset)


def main():
    df = pd.read_csv("player_gameweek_data_position_1.csv")

    for col in FEATURES + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=FEATURES + [TARGET])
    df["form_last_6_gw"] = df["form_last_6_gw"] * 10.0

    train_df = df[df["round"] <= 14]
    val_df   = df[(df["round"] > 14) & (df["round"] <= 20)]

    FEATURES.remove("round")
    FEATURES.remove("element")

    X_train = train_df[FEATURES].values
    y_train = train_df[TARGET].values

    X_val = val_df[FEATURES].values
    y_val = val_df[TARGET].values

    train_ds = PlayerDataset(X_train, y_train)
    val_ds   = PlayerDataset(X_val, y_val)

    train_loader = DataLoader(train_ds, batch_size=len(train_ds), shuffle=True)
    val_loader   = DataLoader(val_ds, batch_size=len(val_ds), shuffle=False)

    model = PlayerRegressor(len(FEATURES)).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.SmoothL1Loss()

    for epoch in range(EPOCHS):
        train_loss = train_epoch(model, train_loader, optimizer, criterion)
        val_loss = eval_epoch(model, val_loader, criterion)

        print(
            f"Epoch {epoch+1:02d} | "
            f"Train MAE: {train_loss:.3f} | "
            f"Val MAE: {val_loss:.3f}"
        )

    torch.save({
        "model_state": model.state_dict(),
        "features": FEATURES
    }, "player_points_model_goalkeepers.pt")

    model.eval()

    example_player = df.iloc[-1:][FEATURES].values

    x = torch.tensor(example_player, dtype=torch.float32).to(DEVICE)

    with torch.no_grad():
        pred = model(x).item()

    print("Predicted points next GW:", round(pred, 2))


if __name__ == "__main__":
    main()
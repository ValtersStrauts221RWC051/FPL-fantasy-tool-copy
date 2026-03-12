import pandas as pd

file = "player_gameweek_data_modified.csv"
df = pd.read_csv(file)

# split by position_id
positions = df['position_id'].unique()

for pos in positions:
    df_pos = df[df['position_id'] == pos]
    df_pos.to_csv(f"player_gameweek_data_position_{pos}.csv", index=False)

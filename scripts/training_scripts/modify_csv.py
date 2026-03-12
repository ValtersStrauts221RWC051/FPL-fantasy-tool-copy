import pandas as pd

file = "player_gameweek_data.csv"
df = pd.read_csv(file)
df_modified = df.drop(columns=["fixture", "opponent_team", "was_home", "kickoff_time", "team_a_score", "team_h_score", "modified", "selected", "transfers_in", "transfers_out", "transfers_balance"])
df_modified.to_csv("player_gameweek_data_modified.csv", index=False) 
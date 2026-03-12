import requests

FPL_BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

response = requests.get(FPL_BOOTSTRAP_URL)
response.raise_for_status()  # raises error if request failed

data = response.json()

# Core data
players = data["elements"]              # All players
teams = data["teams"]                   # Premier League teams
positions = data["element_types"]       # Positions (GK, DEF, MID, FWD)
events = data["events"]                 # Gameweeks
game_settings = data["game_settings"]   # Global FPL rules
phases = data["phases"]                 # Season phases
total_players = data["total_players"]   # Total FPL users

import pandas as pd
from tqdm import tqdm

master_df = pd.DataFrame()

for player in tqdm(players):
    print(f"Player Name: {player['first_name']} {player['second_name']}, Position ID: {player['element_type']}")
    id = player['id']
    URL_STATS = f"https://fantasy.premierleague.com/api/element-summary/{id}/"
    response_stats = requests.get(URL_STATS)
    response_stats.raise_for_status()
    stats_data = response_stats.json()
    history = stats_data["history"]  # Historical performance data

    df_history = pd.DataFrame(history)
    df_history['player_name'] = f"{player['first_name']} {player['second_name']}"
    df_history['position_id'] = player['element_type']

    # Add form as last 6 gw average
    for i in range(len(df_history)):
        if i < 5:
            df_history.at[i, 'form_last_6_gw'] = df_history['total_points'][:i+1].mean()
        else:
            df_history.at[i, 'form_last_6_gw'] = df_history['total_points'][i-5:i+1].mean()

    master_df = pd.concat([master_df, df_history], ignore_index=True)

master_df.to_csv("player_gameweek_data.csv", index=False)
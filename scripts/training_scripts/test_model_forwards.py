import pandas as pd
import torch.nn as nn
import torch
import numpy as np

model_path = "player_points_model_forwards.pt"

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

model_features = torch.load(model_path)

model = PlayerRegressor(n_features=len(model_features['features']))
model_state_dict = model_features['model_state']
model.load_state_dict(model_state_dict)
model.eval()

# use Haaland as example
example_player = [[
    1732/(1732/90),  # minutes
    19/(1732/90),    # goals_scored
    4/(1732/90),     # assists
    0/(1732/90),     # own_goals
    1/(1732/90),     # penalties_missed
    0/(1732/90),     # yellow_cards
    0/(1732/90),     # red_cards
    31/(1732/90),    # bonus
    648/(1732/90),   # bps
    786.0/(1732/90), # influence
    140.7/(1732/90), # creativity
    956.0/(1732/90), # threat
    68/(1732/90),    # defensive_contribution
    16.94/(1732/90), # expected_goals
    1.24/(1732/90),  # expected_assists
    18.18/(1732/90), # expected_goal_involvements
    21.53/(1732/90),  # expected_goals_conceded
    5.8 * 10,             # form_last_6_gw
]]
example_player_tensor = torch.tensor(example_player, dtype=torch.float32)
print("features names:", model_features['features'])

example_player_array = np.array(example_player)
example_player_scaled = example_player_array.copy()
example_player_tensor = torch.tensor(example_player_scaled, dtype=torch.float32)

with torch.no_grad():
    prediction = model(example_player_tensor).item()
print(f"Predicted points for Erling Haaland: {prediction:.2f}")

torch.onnx.export(
    model,
    example_player_tensor,
    "forwards_model.onnx",
    input_names=["input"],
    output_names=["output"],
)


"""
{
      "can_transact": true,
      "can_select": true,
      "chance_of_playing_next_round": 100,
      "chance_of_playing_this_round": 100,
      "code": 223094,
      "cost_change_event": 0,
      "cost_change_event_fall": 0,
      "cost_change_start": 11,
      "cost_change_start_fall": -11,
      "dreamteam_count": 8,
      "element_type": 4,
      "ep_next": "6.3",
      "ep_this": "6.3",
      "event_points": 0,
      "first_name": "Erling",
      "form": "5.8",
      "id": 430,
      "in_dreamteam": true,
      "news": "",
      "news_added": "2025-09-24T06:00:06.159318Z",
      "now_cost": 151,
      "photo": "223094.jpg",
      "points_per_game": "7.8",
      "removed": false,
      "second_name": "Haaland",
      "selected_by_percent": "74.2",
      "special": false,
      "squad_number": null,
      "status": "a",
      "team": 13,
      "team_code": 43,
      "total_points": 157,
      "transfers_in": 6573240,
      "transfers_in_event": 1603,
      "transfers_out": 923116,
      "transfers_out_event": 903,
      "value_form": "0.4",
      "value_season": "10.4",
      "web_name": "Haaland",
      "region": 161,
      "team_join_date": "2022-07-01",
      "birth_date": "2000-07-21",
      "has_temporary_code": false,
      "opta_code": "p223094",
      "minutes": 1732,
      "goals_scored": 19,
      "assists": 4,
      "clean_sheets": 10,
      "goals_conceded": 17,
      "own_goals": 0,
      "penalties_saved": 0,
      "penalties_missed": 1,
      "yellow_cards": 0,
      "red_cards": 0,
      "saves": 0,
      "bonus": 31,
      "bps": 648,
      "influence": "786.0",
      "creativity": "140.7",
      "threat": "956.0",
      "ict_index": "188.4",
      "clearances_blocks_interceptions": 33,
      "recoveries": 25,
      "tackles": 10,
      "defensive_contribution": 68,
      "starts": 20,
      "expected_goals": "16.94",
      "expected_assists": "1.24",
      "expected_goal_involvements": "18.18",
      "expected_goals_conceded": "21.53",
      "corners_and_indirect_freekicks_order": null,
      "corners_and_indirect_freekicks_text": "",
      "direct_freekicks_order": null,
      "direct_freekicks_text": "",
      "penalties_order": 1,
      "penalties_text": "",
      "scout_risks": [],
      "influence_rank": 1,
      "influence_rank_type": 1,
      "creativity_rank": 155,
      "creativity_rank_type": 11,
      "threat_rank": 1,
      "threat_rank_type": 1,
      "ict_index_rank": 1,
      "ict_index_rank_type": 1,
      "expected_goals_per_90": 0.88,
      "saves_per_90": 0.0,
      "expected_assists_per_90": 0.06,
      "expected_goal_involvements_per_90": 0.94,
      "expected_goals_conceded_per_90": 1.12,
      "goals_conceded_per_90": 0.88,
      "now_cost_rank": 1,
      "now_cost_rank_type": 1,
      "form_rank": 7,
      "form_rank_type": 1,
      "points_per_game_rank": 1,
      "points_per_game_rank_type": 1,
      "selected_rank": 1,
      "selected_rank_type": 1,
      "starts_per_90": 1.04,
      "clean_sheets_per_90": 0.52,
      "defensive_contribution_per_90": 3.53
    },

    per 90 minutes:
    "minutes": 1732/(1732/90),
    "goals_scored": 19/(1732/90),
    "assists": 4/(1732/90),
    "own_goals": 0/(1732/90),
    "penalties_missed": 1/(1732/90),
    "yellow_cards": 0/(1732/90),
    "red_cards": 0/(1732/90),
    "bonus": 31/(1732/90),
    "bps": 648/(1732/90),
    "influence": 786.0/(1732/90),
    "creativity": 140.7/(1732/90),
    "threat": 956.0/(1732/90),
    "defensive_contribution": 68/(1732/90),
    "expected_goals": 16.94/(1732/90),
    "expected_assists": 1.24/(1732/90),
    "expected_goal_involvements": 18.18/(1732/90),
    "expected_goals_conceded": 21.53/(1732/90),
    "form_last_6_gw": 5.8
"""

# ------------------------------

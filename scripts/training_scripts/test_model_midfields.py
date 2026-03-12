import torch.nn as nn
import torch
import numpy as np

model_path = "player_points_model_midfields.pt"

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

example_player = [[
    1343/(1343/90),  # minutes
    4/(1343/90),  # goals_scored
    7/(1343/90),  # assists
    7/(1343/90),  # clean_sheets
    0/(1343/90),  # own_goals
    0/(1343/90),  # penalties_missed
    1/(1343/90),  # yellow_cards
    0/(1343/90),  # red_cards
    10/(1343/90),  # bonus
    357/(1343/90),  # bps
    379.0/(1343/90),  # influence
    530.0/(1343/90),  # creativity
    492.0/(1343/90),  # threat
    106/(1343/90),  # defensive_contribution
    5.25/(1343/90),  # expected_goals
    4.28/(1343/90),  # expected_assists
    9.53/(1343/90),  # expected_goal_involvements
    8.84/(1343/90),  # expected_goals_conceded
    5.2 * 10         # form_last_6_gw
]]
example_player_tensor = torch.tensor(example_player, dtype=torch.float32)
print("features names:", model_features['features'])

example_player_array = np.array(example_player)
example_player_scaled = example_player_array.copy()
example_player_tensor = torch.tensor(example_player_scaled, dtype=torch.float32)


with torch.no_grad():
    prediction = model(example_player_tensor).item()
print(f"Predicted points for Bukayo Saka: {prediction:.2f}")

torch.onnx.export(
    model,
    example_player_tensor,
    "midfields_model.onnx",
    input_names=["input"],
    output_names=["output"],
)


"""
    {
      "can_transact": true,
      "can_select": true,
      "chance_of_playing_next_round": 100,
      "chance_of_playing_this_round": 100,
      "code": 223340,
      "cost_change_event": 0,
      "cost_change_event_fall": 0,
      "cost_change_start": 2,
      "cost_change_start_fall": -2,
      "dreamteam_count": 1,
      "element_type": 3,
      "ep_next": "6.2",
      "ep_this": "5.7",
      "event_points": 0,
      "first_name": "Bukayo",
      "form": "5.2",
      "id": 16,
      "in_dreamteam": false,
      "news": "",
      "news_added": "2025-08-23T22:30:05.759392Z",
      "now_cost": 102,
      "photo": "223340.jpg",
      "points_per_game": "5.3",
      "removed": false,
      "second_name": "Saka",
      "selected_by_percent": "20.4",
      "special": false,
      "squad_number": null,
      "status": "a",
      "team": 1,
      "team_code": 3,
      "total_points": 95,
      "transfers_in": 3820501,
      "transfers_in_event": 2174,
      "transfers_out": 3180280,
      "transfers_out_event": 4505,
      "value_form": "0.5",
      "value_season": "9.3",
      "web_name": "Saka",
      "region": 241,
      "team_join_date": "2018-11-28",
      "birth_date": "2001-09-05",
      "has_temporary_code": false,
      "opta_code": "p223340",
      "minutes": 1343,
      "goals_scored": 4,
      "assists": 7,
      "clean_sheets": 7,
      "goals_conceded": 9,
      "own_goals": 0,
      "penalties_saved": 0,
      "penalties_missed": 0,
      "yellow_cards": 1,
      "red_cards": 0,
      "saves": 0,
      "bonus": 10,
      "bps": 357,
      "influence": "379.0",
      "creativity": "530.0",
      "threat": "492.0",
      "ict_index": "140.1",
      "clearances_blocks_interceptions": 8,
      "recoveries": 73,
      "tackles": 25,
      "defensive_contribution": 106,
      "starts": 15,
      "expected_goals": "5.25",
      "expected_assists": "4.28",
      "expected_goal_involvements": "9.53",
      "expected_goals_conceded": "8.84",
      "corners_and_indirect_freekicks_order": 2,
      "corners_and_indirect_freekicks_text": "",
      "direct_freekicks_order": null,
      "direct_freekicks_text": "",
      "penalties_order": 1,
      "penalties_text": "",
      "scout_risks": [],
      "influence_rank": 59,
      "influence_rank_type": 15,
      "creativity_rank": 7,
      "creativity_rank_type": 7,
      "threat_rank": 11,
      "threat_rank_type": 5,
      "ict_index_rank": 7,
      "ict_index_rank_type": 5,
      "expected_goals_per_90": 0.35,
      "saves_per_90": 0.0,
      "expected_assists_per_90": 0.29,
      "expected_goal_involvements_per_90": 0.64,
      "expected_goals_conceded_per_90": 0.59,
      "goals_conceded_per_90": 0.6,
      "now_cost_rank": 5,
      "now_cost_rank_type": 3,
      "form_rank": 17,
      "form_rank_type": 10,
      "points_per_game_rank": 11,
      "points_per_game_rank_type": 7,
      "selected_rank": 16,
      "selected_rank_type": 5,
      "starts_per_90": 1.01,
      "clean_sheets_per_90": 0.47,
      "defensive_contribution_per_90": 7.1
    },

    per 90 minutes:
    "minutes", : 1343/(1343/90),
    "goals_scored", : 4/(1343/90),
    "assists", : 7/(1343/90),
    "clean_sheets", : 7/(1343/90),
    "own_goals", : 0/(1343/90),
    "penalties_missed", : 0/(1343/90),
    "yellow_cards", : 1/(1343/90),
    "red_cards", : 0/(1343/90),
    "bonus", : 10/(1343/90),
    "bps", : 357/(1343/90),
    "influence", : 379.0/(1343/90),
    "creativity", : 530.0/(1343/90),
    "threat", : 492.0/(1343/90),
    "defensive_contribution", : 106/(1343/90),
    "expected_goals", : 5.25/(1343/90),
    "expected_assists", : 4.28/(1343/90),
    "expected_goal_involvements", : 9.53/(1343/90),
    "expected_goals_conceded", : 8.84/(1343/90),
    "form_last_6_gw" : 5.2 * 10
"""

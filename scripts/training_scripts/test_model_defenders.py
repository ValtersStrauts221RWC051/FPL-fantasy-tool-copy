import torch.nn as nn
import torch
import numpy as np

model_path = "player_points_model_defenders.pt"

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
    1800/(1800/90),  # minutes
    0/(1800/90),  # goals_scored
    0/(1800/90),  # assists
    6/(1800/90),  # clean_sheets
    28/(1800/90),  # goals_conceded
    0/(1800/90),  # own_goals
    0/(1800/90),  # penalties_missed
    3/(1800/90),  # yellow_cards
    0/(1800/90),  # red_cards
    4/(1800/90),  # bonus
    286/(1800/90),  # bps
    555.6/(1800/90),  # influence
    113.6/(1800/90),  # creativity
    142.0/(1800/90),  # threat
    194/(1800/90),  # defensive_contribution
    0.92/(1800/90),  # expected_goals
    0.57/(1800/90),  # expected_assists
    1.49/(1800/90),  # expected_goal_involvements
    23.23/(1800/90),  # expected_goals_conceded
    2.8 * 10  # form_last_6_gw
]]
example_player_tensor = torch.tensor(example_player, dtype=torch.float32)
print("features names:", model_features['features'])

example_player_array = np.array(example_player)
example_player_scaled = example_player_array.copy()
example_player_tensor = torch.tensor(example_player_scaled, dtype=torch.float32)


with torch.no_grad():
    prediction = model(example_player_tensor).item()
print(f"Predicted points for Virgil Van Dijk: {prediction:.2f}")

torch.onnx.export(
    model,
    example_player_tensor,
    "defenders_model.onnx",
    input_names=["input"],
    output_names=["output"],
)


"""
    {
      "can_transact": true,
      "can_select": true,
      "chance_of_playing_next_round": null,
      "chance_of_playing_this_round": null,
      "code": 97032,
      "cost_change_event": 0,
      "cost_change_event_fall": 0,
      "cost_change_start": -1,
      "cost_change_start_fall": 1,
      "dreamteam_count": 0,
      "element_type": 2,
      "ep_next": "3.3",
      "ep_this": "2.3",
      "event_points": 0,
      "first_name": "Virgil",
      "form": "2.8",
      "id": 373,
      "in_dreamteam": false,
      "news": "",
      "news_added": null,
      "now_cost": 59,
      "photo": "97032.jpg",
      "points_per_game": "3.6",
      "removed": false,
      "second_name": "van Dijk",
      "selected_by_percent": "22.3",
      "special": false,
      "squad_number": null,
      "status": "a",
      "team": 12,
      "team_code": 14,
      "total_points": 73,
      "transfers_in": 2507453,
      "transfers_in_event": 2612,
      "transfers_out": 2969157,
      "transfers_out_event": 2914,
      "value_form": "0.5",
      "value_season": "12.4",
      "web_name": "Virgil",
      "region": 152,
      "team_join_date": "2018-01-01",
      "birth_date": "1991-07-08",
      "has_temporary_code": false,
      "opta_code": "p97032",
      "minutes": 1800,
      "goals_scored": 0,
      "assists": 0,
      "clean_sheets": 6,
      "goals_conceded": 28,
      "own_goals": 0,
      "penalties_saved": 0,
      "penalties_missed": 0,
      "yellow_cards": 3,
      "red_cards": 0,
      "saves": 0,
      "bonus": 4,
      "bps": 286,
      "influence": "555.6",
      "creativity": "113.6",
      "threat": "142.0",
      "ict_index": "81.0",
      "clearances_blocks_interceptions": 179,
      "recoveries": 42,
      "tackles": 15,
      "defensive_contribution": 194,
      "starts": 20,
      "expected_goals": "0.92",
      "expected_assists": "0.57",
      "expected_goal_involvements": "1.49",
      "expected_goals_conceded": "23.23",
      "corners_and_indirect_freekicks_order": null,
      "corners_and_indirect_freekicks_text": "",
      "direct_freekicks_order": null,
      "direct_freekicks_text": "",
      "penalties_order": null,
      "penalties_text": "",
      "scout_risks": [],
      "influence_rank": 7,
      "influence_rank_type": 3,
      "creativity_rank": 180,
      "creativity_rank_type": 44,
      "threat_rank": 129,
      "threat_rank_type": 22,
      "ict_index_rank": 55,
      "ict_index_rank_type": 9,
      "expected_goals_per_90": 0.05,
      "saves_per_90": 0.0,
      "expected_assists_per_90": 0.03,
      "expected_goal_involvements_per_90": 0.08,
      "expected_goals_conceded_per_90": 1.16,
      "goals_conceded_per_90": 1.4,
      "now_cost_rank": 89,
      "now_cost_rank_type": 5,
      "form_rank": 111,
      "form_rank_type": 40,
      "points_per_game_rank": 114,
      "points_per_game_rank_type": 45,
      "selected_rank": 15,
      "selected_rank_type": 5,
      "starts_per_90": 1.0,
      "clean_sheets_per_90": 0.3,
      "defensive_contribution_per_90": 9.7
    },

    per 90 minutes:
    "minutes", : 1800/(1800/90),
    "goals_scored", : 0/(1800/90),
    "assists", : 0/(1800/90),
    "clean_sheets", : 6/(1800/90),
    "goals_conceded", : 28/(1800/90),
    "own_goals", : 0/(1800/90),
    "penalties_missed", : 0/(1800/90),
    "yellow_cards", : 3/(1800/90),
    "red_cards", : 0/(1800/90),
    "bonus", : 4/(1800/90),
    "bps", : 286/(1800/90),
    "influence", : 555.6/(1800/90),
    "creativity", : 113.6/(1800/90),
    "threat", : 142.0/(1800/90),
    "defensive_contribution", : 194/(1800/90),
    "expected_goals", : 0.92/(1800/90),
    "expected_assists", : 0.57/(1800/90),
    "expected_goal_involvements", : 1.49/(1800/90),
    "expected_goals_conceded", : 23.23/(1800/90),
    "form_last_6_gw" : 2.8 * 10
"""

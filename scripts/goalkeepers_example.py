import numpy as np
import onnxruntime

model_path = "goalkeepers_model.onnx"

dummy_input = [[
    1440/(1440/90),  # minutes
    0/(1440/90),  # assists
    4/(1440/90),  # clean_sheets
    16/(1440/90),  # goals_conceded
    0/(1440/90),  # own_goals
    1/(1440/90),  # penalties_saved
    0/(1440/90),  # penalties_missed
    1/(1440/90),  # yellow_cards
    0/(1440/90),  # red_cards
    48/(1440/90),  # saves
    3/(1440/90),  # bonus
    269/(1440/90),  # bps
    367.6/(1440/90),  # influence
    3.0/(1440/90),  # creativity
    0.0/(1440/90),  # threat
    0/(1440/90),  # defensive_contribution
    0.03/(1440/90),  # expected_assists
    0.03/(1440/90),  # expected_goal_involvements
    22.01/(1440/90),  # expected_goals_conceded
    1.5 * 10  # form_last_6_gw
]]

dummy_input_array = np.array(dummy_input, dtype=np.float32)

ort_session = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])
ort_inputs = {ort_session.get_inputs()[0].name: dummy_input_array}
ort_outs = ort_session.run(None, ort_inputs)
print(f"Predicted_points for Martinez: {ort_outs[0][0][0]:.2f}")


"""
    {
      "can_transact": true,
      "can_select": true,
      "chance_of_playing_next_round": 100,
      "chance_of_playing_this_round": 100,
      "code": 98980,
      "cost_change_event": 0,
      "cost_change_event_fall": 0,
      "cost_change_start": 0,
      "cost_change_start_fall": 0,
      "dreamteam_count": 2,
      "element_type": 1,
      "ep_next": "1.5",
      "ep_this": "1.5",
      "event_points": 0,
      "first_name": "Emiliano",
      "form": "1.5",
      "id": 32,
      "in_dreamteam": false,
      "news": "",
      "news_added": "2025-12-12T00:00:09.834522Z",
      "now_cost": 50,
      "photo": "98980.jpg",
      "points_per_game": "3.9",
      "removed": false,
      "second_name": "Mart\u00ednez Romero",
      "selected_by_percent": "3.6",
      "special": false,
      "squad_number": null,
      "status": "a",
      "team": 2,
      "team_code": 7,
      "total_points": 63,
      "transfers_in": 631384,
      "transfers_in_event": 1285,
      "transfers_out": 431897,
      "transfers_out_event": 594,
      "value_form": "0.3",
      "value_season": "12.6",
      "web_name": "Martinez",
      "region": 10,
      "team_join_date": "2020-09-16",
      "birth_date": "1992-09-02",
      "has_temporary_code": false,
      "opta_code": "p98980",
      "minutes": 1440,
      "goals_scored": 0,
      "assists": 0,
      "clean_sheets": 4,
      "goals_conceded": 16,
      "own_goals": 0,
      "penalties_saved": 1,
      "penalties_missed": 0,
      "yellow_cards": 1,
      "red_cards": 0,
      "saves": 48,
      "bonus": 3,
      "bps": 269,
      "influence": "367.6",
      "creativity": "3.0",
      "threat": "0.0",
      "ict_index": "37.0",
      "clearances_blocks_interceptions": 13,
      "recoveries": 129,
      "tackles": 0,
      "defensive_contribution": 0,
      "starts": 16,
      "expected_goals": "0.00",
      "expected_assists": "0.03",
      "expected_goal_involvements": "0.03",
      "expected_goals_conceded": "22.01",
      "corners_and_indirect_freekicks_order": null,
      "corners_and_indirect_freekicks_text": "",
      "direct_freekicks_order": null,
      "direct_freekicks_text": "",
      "penalties_order": null,
      "penalties_text": "",
      "scout_risks": [],
      "influence_rank": 67,
      "influence_rank_type": 13,
      "creativity_rank": 423,
      "creativity_rank_type": 12,
      "threat_rank": 741,
      "threat_rank_type": 84,
      "ict_index_rank": 237,
      "ict_index_rank_type": 13,
      "expected_goals_per_90": 0.0,
      "saves_per_90": 3.0,
      "expected_assists_per_90": 0.0,
      "expected_goal_involvements_per_90": 0.0,
      "expected_goals_conceded_per_90": 1.38,
      "goals_conceded_per_90": 1.0,
      "now_cost_rank": 242,
      "now_cost_rank_type": 8,
      "form_rank": 220,
      "form_rank_type": 17,
      "points_per_game_rank": 86,
      "points_per_game_rank_type": 6,
      "selected_rank": 95,
      "selected_rank_type": 15,
      "starts_per_90": 1.0,
      "clean_sheets_per_90": 0.25,
      "defensive_contribution_per_90": 0.0
    },

    per 90 minutes:
    "minutes", : 1440/(1440/90),
    "assists", : 0/(1440/90),
    "clean_sheets", : 4/(1440/90),
    "goals_conceded", : 16/(1440/90),
    "own_goals", : 0/(1440/90),
    "penalties_saved", : 1/(1440/90),
    "penalties_missed", : 0/(1440/90),
    "yellow_cards", : 1/(1440/90),
    "red_cards", : 0/(1440/90),
    "saves", : 48/(1440/90),
    "bonus", : 3/(1440/90),
    "bps", : 269/(1440/90),
    "influence", : 367.6/(1440/90),
    "creativity", : 3.0/(1440/90),
    "threat", : 0.0/(1440/90),
    "defensive_contribution", : 0/(1440/90),
    "expected_assists", : 0.03/(1440/90),
    "expected_goal_involvements", : 0.03/(1440/90),
    "expected_goals_conceded", : 22.01/(1440/90),
    "form_last_6_gw" : 1.5 * 10
"""


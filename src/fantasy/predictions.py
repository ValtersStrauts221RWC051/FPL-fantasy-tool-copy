import numpy as np
import onnxruntime
import os

from fantasy.models import Player

# Get path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/fantasy
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../models"))  # normalize path

# Paths to models
goalkeeper_model_path = os.path.join(MODEL_DIR, "goalkeepers_model.onnx")
defender_model_path = os.path.join(MODEL_DIR, "defenders_model.onnx")
midfielder_model_path = os.path.join(MODEL_DIR, "midfields_model.onnx")
forward_model_path = os.path.join(MODEL_DIR, "forwards_model.onnx")
    
MODEL_PATHS = {
    "Goalkeeper": goalkeeper_model_path,
    "Defender": defender_model_path,
    "Midfielder": midfielder_model_path,
    "Forward": forward_model_path,
}

def predict_player_points(player):
    # Pick the model based on player's position
    model_path = MODEL_PATHS.get(player.position.name)
    if not model_path:
        raise ValueError(f"No model defined for position: {player.position.name}")

    # Prepare the input array
    input_data = get_input_data(player)
    input_array = np.array(input_data, dtype=np.float32)

    # Run ONNX inference
    ort_session = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    ort_inputs = {ort_session.get_inputs()[0].name: input_array}
    ort_outs = ort_session.run(None, ort_inputs)

    return ort_outs[0][0, 0]


def get_input_data(player):
    MIN_PLAYED_MINUTES = 360  # adjust as you see fit

    played_minutes = max(player.minutes, MIN_PLAYED_MINUTES)
    normalization = played_minutes / 90

    if player.position.name == "Midfielder":
        return [[
            player.minutes / normalization,
            player.goals_scored / normalization,
            player.assists / normalization,
            player.clean_sheets / normalization,
            player.own_goals / normalization,
            player.penalties_missed / normalization,
            player.yellow_cards / normalization,
            player.red_cards / normalization,
            player.bonus / normalization,
            player.bps / normalization,
            player.influence / normalization,
            player.creativity / normalization,
            player.threat / normalization,
            player.defensive_contribution / normalization,
            player.expected_goals / normalization,
            player.expected_assists / normalization,
            player.expected_goal_involvements / normalization,
            player.expected_goals_conceded / normalization,
            player.form * 10  # last_6_gw form normalization
        ]]

    elif player.position.name == "Forward":
        return [[
            player.minutes / normalization,
            player.goals_scored / normalization,
            player.assists / normalization,
            player.own_goals / normalization,
            player.penalties_missed / normalization,
            player.yellow_cards / normalization,
            player.red_cards / normalization,
            player.bonus / normalization,
            player.bps / normalization,
            player.influence / normalization,
            player.creativity / normalization,
            player.threat / normalization,
            player.defensive_contribution / normalization,
            player.expected_goals / normalization,
            player.expected_assists / normalization,
            player.expected_goal_involvements / normalization,
            player.expected_goals_conceded / normalization,
            player.form * 10  # last_6_gw form normalization
        ]]
    
    elif player.position.name == "Defender":
        return [[
            player.minutes / normalization,
            player.goals_scored / normalization,
            player.assists / normalization,
            player.clean_sheets / normalization,
            player.goals_conceded / normalization,
            player.own_goals / normalization,
            player.penalties_missed / normalization,
            player.yellow_cards / normalization,
            player.red_cards / normalization,
            player.bonus / normalization,
            player.bps / normalization,
            player.influence / normalization,
            player.creativity / normalization,
            player.threat / normalization,
            player.defensive_contribution / normalization,
            player.expected_goals / normalization,
            player.expected_assists / normalization,
            player.expected_goal_involvements / normalization,
            player.expected_goals_conceded / normalization,
            player.form * 10  # last_6_gw form normalization
        ]]
    
    elif player.position.name == "Goalkeeper":
        return [[
            player.minutes / normalization,
            player.assists / normalization,
            player.clean_sheets / normalization,
            player.goals_conceded / normalization,
            player.own_goals / normalization,
            player.penalties_saved / normalization,
            player.penalties_missed / normalization,
            player.yellow_cards / normalization,
            player.saves / normalization,
            player.red_cards / normalization,
            player.bonus / normalization,
            player.bps / normalization,
            player.influence / normalization,
            player.creativity / normalization,
            player.threat / normalization,
            player.defensive_contribution / normalization,
            player.expected_assists / normalization,
            player.expected_goal_involvements / normalization,
            player.expected_goals_conceded / normalization,
            player.form * 10  # last_6_gw form normalization
        ]]
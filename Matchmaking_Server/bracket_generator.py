# bracket_generator.py

import math
import random
from typing import List, Dict, Any

def generate_bracket(players: List[str]) -> Dict[str, Any]:
    """Generate a single elimination bracket from a list of player names."""
    random.shuffle(players)
    n = len(players)
    next_power = 2 ** math.ceil(math.log2(n))
    byes = next_power - n
    full_players = players + [None] * byes

    participants = []
    participant_map = {}
    for i, name in enumerate(full_players):
        pid = i + 1
        if name:
            participants.append({"id": pid, "name": name})
            participant_map[i] = pid
        else:
            participant_map[i] = None

    all_rounds = [{"p1": participant_map[i], "p2": participant_map[i+1]}
                  for i in range(0, len(participant_map), 2)]

    matches = []
    match_id = 1
    stage_id = 1

    current_round = all_rounds
    round_number = 1

    while current_round:
        for match in current_round:
            matches.append({
                "id": match_id,
                "stage_id": stage_id,
                "round": round_number,
                "group": 0,
                "child_count": 1,
                "status": 0,
                "opponent1": {"id": match["p1"], "score": None} if match["p1"] else None,
                "opponent2": {"id": match["p2"], "score": None} if match["p2"] else None
            })
            match_id += 1

        next_round_size = len(current_round) // 2
        current_round = [{"p1": None, "p2": None} for _ in range(next_round_size)]
        round_number += 1
        if next_round_size == 0:
            break

    return {
        "stages": [{
            "id": stage_id,
            "name": "Main",
            "tournament_id": 0,
            "type": "single_elimination",
            "number": 1
        }],
        "matches": matches,
        "participants": participants
    }

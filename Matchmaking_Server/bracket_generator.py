from typing import List, Dict, Any
import math
import random

def generate_bracket(players: List[str]) -> Dict[str, Any]:
    """Generate a single elimination bracket from a list of player names."""
    if not players or len(players) < 2:
        return {
            "stages": [],
            "matches": [],
            "participants": [],
            "error": "At least two players are required to generate a bracket."
        }

    players = [p for p in players if isinstance(p, str) and p.strip()]
    if len(players) < 2:
        return {
            "stages": [],
            "matches": [],
            "participants": [],
            "error": "Invalid player names."
        }

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
            participant_map[i] = {"id": pid, "name": name}
        else:
            participant_map[i] = None

    matches = []
    match_id = 1
    stage_id = 1
    round_number = 1

    def build_round(pairs):
        return [{"p1": pairs[i], "p2": pairs[i + 1] if i + 1 < len(pairs) else None}
                for i in range(0, len(pairs), 2)]

    current_round = build_round(list(participant_map.values()))

    while current_round:
        next_pairs = []
        for match in current_round:
            matches.append({
                "id": match_id,
                "stage_id": stage_id,
                "round": round_number,
                "group": 0,
                "child_count": 1,
                "status": 0,
                "opponent1": match["p1"],
                "opponent2": match["p2"]
            })
            match_id += 1
            next_pairs.append(None)  # Placeholder for future winners

        if len(next_pairs) <= 1:
            break

        current_round = build_round(next_pairs)
        round_number += 1

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

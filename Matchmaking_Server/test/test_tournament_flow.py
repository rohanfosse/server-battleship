import requests
import time
import pytest

SERVER_URL = "http://localhost:5000"

players = [
    {"username": "Alice", "port": 8001},
    {"username": "Bob", "port": 8002},
    {"username": "Carol", "port": 8003},
    {"username": "Dan", "port": 8004},
    {"username": "Eve", "port": 8005},
    {"username": "Frank", "port": 8006},
    {"username": "Grace", "port": 8007},
    {"username": "Hank", "port": 8008}
]

def test_register_players():
    for player in players:
        r = requests.post(f"{SERVER_URL}/auto_join", json=player)
        assert r.status_code == 200
        time.sleep(0.05)

def test_start_tournament():
    r = requests.post(f"{SERVER_URL}/start_tournament")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "tournament_started"
    assert len(data["players"]) == len(players)

def test_simulate_match_results():
    r = requests.get(f"{SERVER_URL}/bracket_data")
    assert r.status_code == 200
    bracket = r.json()
    matches = bracket.get("matches", [])
    rounds = sorted(set(m["round"] for m in matches if m.get("round") is not None))

    # Simule tous les matchs de tous les rounds
    for rnd in rounds:
        current_matches = [m for m in matches if m["round"] == rnd]
        for match in current_matches:
            op1 = match.get("opponent1") or {}
            op2 = match.get("opponent2") or {}
            p1 = op1.get("name")
            p2 = op2.get("name")
            if p1 and p2 and not op1.get("result") and not op2.get("result"):
                winner = p1
                loser = p2
                # Lancer le match
                requests.post(f"{SERVER_URL}/start_tournament_match", json={
                    "player1": p1,
                    "player2": p2,
                    "match_id": match["id"]
                })
                # Soumettre le résultat
                res = requests.post(f"{SERVER_URL}/match_result", json={
                    "winner": winner,
                    "loser": loser
                })
                assert res.status_code == 200
                assert res.json()["status"] == "result recorded"
                time.sleep(0.05)

def test_final_winner():
    r = requests.get(f"{SERVER_URL}/bracket_data")
    assert r.status_code == 200
    bracket = r.json()
    matches = bracket.get("matches", [])

    if not matches:
        pytest.skip("No bracket matches available")

    max_round = max(m["round"] for m in matches)
    final_matches = [m for m in matches if m["round"] == max_round]
    assert len(final_matches) == 1
    final = final_matches[0]

    op1 = final.get("opponent1") or {}
    op2 = final.get("opponent2") or {}

    if not op1 or not op2:
        pytest.skip("Final not yet filled")

    winner = None
    if op1.get("result") == "win":
        winner = op1.get("name")
    elif op2.get("result") == "win":
        winner = op2.get("name")

    assert winner is not None, "No winner declared in the final match"
    print(f"🏆 Final winner is {winner}")

def test_stats_endpoint():
    r = requests.get(f"{SERVER_URL}/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_matches" in data
    assert isinstance(data["total_matches"], int)
    assert "win_percentages" in data

def test_scores_history():
    r = requests.get(f"{SERVER_URL}/scores_history")
    assert r.status_code == 200
    data = r.json()
    assert "scores" in data
    assert isinstance(data["scores"], list)
    assert "history" in data


import requests

BASE_URL = "http://localhost:5000"

def test_auto_join_multiple_players():
    players = [
        {"username": "Test1", "port": 9001},
        {"username": "Test2", "port": 9002},
        {"username": "Test3", "port": 9003},
        {"username": "Test4", "port": 9004}
    ]
    for player in players:
        r = requests.post(f"{BASE_URL}/auto_join", json=player)
        assert r.status_code == 200
        assert r.json().get("status") == "connected"

def test_start_tournament():
    r = requests.post(f"{BASE_URL}/start_tournament")
    assert r.status_code == 200
    assert r.json().get("status") == "tournament_started"

def test_bracket_generation_after_start():
    r = requests.get(f"{BASE_URL}/bracket_data")
    data = r.json()
    assert "participants" in data
    assert len(data["participants"]) >= 2
    assert len(data["matches"]) > 0

def test_reset_tournament():
    r = requests.post(f"{BASE_URL}/reset_tournament")
    assert r.status_code == 200
    assert r.json().get("status") == "tournament_reset"

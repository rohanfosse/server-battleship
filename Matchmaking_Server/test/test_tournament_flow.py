import requests
import time
import random

SERVER_URL = "http://localhost:5000"

# List of 8 players to simulate tournament
players = [
    {"username": "Alice", "port": 8001},
    {"username": "Bob", "port": 8002},
    {"username": "Carol", "port": 8003},
    {"username": "Dan", "port": 8004},
    {"username": "Eve", "port": 8005},
    {"username": "Frank", "port": 8006},
    {"username": "Grace", "port": 8007},
    {"username": "Hank", "port": 8008},
]

def register_players():
    print("🎮 Registering players...")
    for player in players:
        r = requests.post(f"{SERVER_URL}/auto_join", json=player)
        status = "✅" if r.status_code == 200 else "❌"
        print(f"{status} {player['username']}")
        time.sleep(0.2)

def launch_tournament():
    print("\n🚀 Launching tournament...")
    r = requests.post(f"{SERVER_URL}/start_tournament")
    if r.status_code == 200:
        print("✅ Tournament started")
    else:
        print(f"❌ Error launching tournament: {r.text}")

def reset_tournament():
    print("\n🔁 Resetting tournament...")
    r = requests.post(f"{SERVER_URL}/reset_tournament")
    if r.status_code == 200:
        print("✅ Tournament reset")
    else:
        print(f"❌ Error resetting tournament: {r.text}")

def check_status():
    r = requests.get(f"{SERVER_URL}/tournament_status")
    data = r.json()
    print(f"\n📊 Status: {'STARTED' if data['started'] else 'NOT STARTED'}")
    print(f"👥 Players: {data['player_count']}")
    print(f"🕒 Start time: {data['started_at']}\n")

def validate_bracket_structure():
    """Ensure that the bracket data structure is valid"""
    r = requests.get(f"{SERVER_URL}/bracket_data")
    data = r.json()
    rounds = data.get('matches', [])
    round_count = len(rounds)

    assert round_count > 0, "No rounds found in the bracket"
    assert round_count > 1, "There should be more than one round in the bracket"

    # Check that rounds 2 and 3 are not empty
    for round_num in [2, 3]:
        assert any(match["round"] == round_num for match in rounds), f"Round {round_num} is empty"

def validate_final_round():
    """Ensure there's exactly one match in the final round"""
    r = requests.get(f"{SERVER_URL}/bracket_data")
    data = r.json()
    final_round = [match for match in data.get('matches', []) if match["round"] == max(match["round"] for match in data["matches"])]
    assert len(final_round) == 1, "There should be exactly one match in the final round"

def simulate_match_results():
    """Simulate match results and move players to next round"""
    print("\n🧑‍🤝‍🧑 Simulating matches...")
    # Get the rounds and simulate results for each match
    r = requests.get(f"{SERVER_URL}/bracket_data")
    data = r.json()
    rounds = data.get('matches', [])

    for match in rounds:
        # Ensure opponents exist
        if match['opponent1'] and match['opponent2']:
            p1 = match['opponent1']['name']
            p2 = match['opponent2']['name']

            # Skip if any of the opponents are TBD or missing
            if p1 == "TBD" or p2 == "TBD" or p1 == "BYE" or p2 == "BYE":
                continue  # Skip match if players are not yet set

            # Simulate a winner randomly
            winner = random.choice([p1, p2])
            loser = p1 if winner == p2 else p2

            # Send match result to the server
            r = requests.post(f"{SERVER_URL}/match_result", json={"winner": winner, "loser": loser})
            if r.status_code == 200:
                print(f"✅ {winner} defeated {loser}")
            else:
                print(f"❌ Error updating match result: {r.text}")
            time.sleep(0.2)

def simulate_multiple_tournaments():
    """Simulate multiple tournaments with shuffled player orders"""
    print("\n🔄 Simulating multiple tournaments...")
    for _ in range(3):  # Run 3 tournaments
        register_players()
        launch_tournament()
        simulate_match_results()
        validate_bracket_structure()
        validate_final_round()
        check_status()
        reset_tournament()

if __name__ == "__main__":
    # 1. Register players
    register_players()

    # 2. Check tournament status
    check_status()

    # 3. Launch tournament
    launch_tournament()

    # 4. Simulate match results
    simulate_match_results()

    # 5. Validate bracket structure and rounds
    validate_bracket_structure()

    # 6. Validate final round has exactly one match
    validate_final_round()

    # 7. Simulate multiple tournaments with random order
    simulate_multiple_tournaments()

    # 8. Check tournament status after reset
    check_status()

    # 9. Reset the tournament
    reset_tournament()
    check_status()

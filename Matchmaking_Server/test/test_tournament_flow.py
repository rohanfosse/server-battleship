import requests
import time

SERVER_URL = "http://localhost:5000"

players = [
    {"username": "Alice", "port": 8001},
    {"username": "Bob", "port": 8002},
    {"username": "Carol", "port": 8003},
    {"username": "Dan", "port": 8004}
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

if __name__ == "__main__":
    register_players()
    check_status()
    launch_tournament()
    time.sleep(2)
    check_status()
    reset_tournament()
    check_status()

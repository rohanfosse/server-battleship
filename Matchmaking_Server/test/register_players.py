import requests
import time

SERVER_URL = "http://localhost:5000"

players = [
    {"username": "Alice", "port": 8001},
    {"username": "Bob", "port": 8002},
    {"username": "Carol", "port": 8003},
    {"username": "Dan", "port": 8004},
    {"username": "Eve", "port": 8005},
    {"username": "Frank", "port": 8006},
    {"username": "Grace", "port": 8007},
    {"username": "Mallory", "port": 8008}
]

def register_players():
    for player in players:
        try:
            print(f"📡 Registering {player['username']}...")
            response = requests.post(
                f"{SERVER_URL}/auto_join",
                json=player
            )
            if response.status_code == 200:
                print(f"✅ Registered {player['username']}")
            else:
                print(f"❌ Error for {player['username']}: {response.text}")
        except Exception as e:
            print(f"❌ Exception for {player['username']}: {e}")
        time.sleep(0.3)  # Small delay to simulate spacing

if __name__ == "__main__":
    register_players()

import requests

SERVER_URL = "http://localhost:5000"

def test_bracket_data():
    print("📡 Testing /bracket_data...")
    r = requests.get(f"{SERVER_URL}/bracket_data")
    data = r.json()

    if "error" in data:
        print(f"⚠️ Not enough players: {data['error']}")
    else:
        print("✅ Bracket generated:")
        print(f"Participants: {len(data['participants'])}")
        print(f"Matches: {len(data['matches'])}")

from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone

app = Flask(__name__)

# === DATA STORES ===

players = {}  # {username: {'ip': ..., 'port': ..., 'joined': ...}}
scores = {}  # {username: score}
matches_history = []  # List of {player1, player2, code, timestamp, winner, duration}
pending_requests = {}  # {to_username: {'from': ..., 'code': ...}}
waiting_matches = {}  # {code: {'creator': username, 'created_at': timestamp}}

# === FRONTEND ROUTES ===

@app.route('/')
def index():
    """Serve the matchmaking dashboard"""
    return render_template('index.html')

@app.route('/admin')
def admin_panel():
    """Serve the admin dashboard"""
    return render_template('admin.html')

@app.route('/admin_data')
def get_admin_data():
    """Send all server state for admin view"""
    active = {
        m["code"]: {"player1": m["player1"], "player2": m["player2"]}
        for m in matches_history if m.get("winner") is None
    }
    return jsonify({
        "waiting": waiting_matches,
        "active": active,
        "history": matches_history,
        "scores": sorted(scores.items(), key=lambda x: -x[1])
    })

# === PLAYER CONNECTION ===

@app.route('/auto_join', methods=['POST'])
def auto_join():
    """Register a player from their local client"""
    data = request.json
    username = data.get("username")
    port = data.get("port")
    ip = request.remote_addr

    if not username or not port:
        return jsonify({'error': 'Missing username or port'}), 400

    players[username] = {
        "ip": ip,
        "port": port,
        "joined": datetime.now().isoformat()
    }
    scores.setdefault(username, 0)

    print(f"[JOIN] {username} connected from {ip}:{port}")
    return jsonify({'status': 'connected', 'player_id': username})

@app.route('/players')
def get_players():
    """Return all currently connected players"""
    return jsonify([
        {"username": u, **info} for u, info in players.items()
    ])

# === MATCHMAKING REQUESTS ===

@app.route('/propose_match', methods=['POST'])
def propose_match():
    """Send a match request from one player to another"""
    data = request.json
    from_player = data.get("from")
    to_player = data.get("to")
    code = data.get("code")

    if not from_player or not to_player:
        return jsonify({'error': 'Missing player names'}), 400
    if to_player not in players:
        return jsonify({'error': 'Target player not found'}), 404

    pending_requests[to_player] = {
        "from": from_player,
        "code": code or None
    }

    return jsonify({'status': 'request sent'})

@app.route('/check_requests/<username>')
def check_requests(username):
    """Check for incoming match requests"""
    req = pending_requests.pop(username, None)
    return jsonify(req or {})

@app.route('/confirm_match', methods=['POST'])
def confirm_match():
    """Start a match after both players agree"""
    data = request.json
    p1 = data.get("player1")
    p2 = data.get("player2")
    code = data.get("code") or f"{p1}_{p2}_{int(datetime.now().timestamp())}"

    matches_history.append({
        "player1": p1,
        "player2": p2,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "winner": None,
        "code": code
    })

    return jsonify({'status': 'match_started', 'match_code': code})

# === MATCHES WITH CODES (PRIVATE MATCHING) ===

@app.route('/create_match', methods=['POST'])
def create_match():
    """Create a private match using a code"""
    data = request.json
    username = data.get("player_id")
    code = data.get("code")

    if not username or not code:
        return jsonify({'error': 'Missing data'}), 400
    if code in waiting_matches:
        return jsonify({'error': 'Code already used'}), 400

    waiting_matches[code] = {
        "creator": username,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    return jsonify({'status': 'waiting', 'code': code})

@app.route('/join_match', methods=['POST'])
def join_match():
    """Join a match using its code"""
    data = request.json
    username = data.get("player_id")
    code = data.get("code")

    if code not in waiting_matches:
        return jsonify({'error': 'Match not found'}), 404

    creator = waiting_matches.pop(code)["creator"]

    matches_history.append({
        "player1": creator,
        "player2": username,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "winner": None,
        "code": code
    })

    return jsonify({'status': 'match_started', 'players': [creator, username]})

@app.route('/match_status')
def match_status():
    """Let the creator poll to see if the match has started"""
    code = request.args.get("code")
    if not code:
        return jsonify({'error': 'Missing code'}), 400

    for match in matches_history:
        if match["code"] == code and match["winner"] is None:
            return jsonify({"status": "active", "opponent": match["player2"]})
    return jsonify({"status": "waiting"})

# === SCORES AND STATS ===

@app.route('/match_result', methods=['POST'])
def match_result():
    """Submit the result of a finished match"""
    data = request.json
    winner = data.get("winner")
    loser = data.get("loser")

    if not winner or not loser:
        return jsonify({'error': 'Missing result data'}), 400

    scores[winner] = scores.get(winner, 0) + 1

    for match in reversed(matches_history):
        if match["winner"] is None and winner in [match["player1"], match["player2"]]:
            match["winner"] = winner
            break

    return jsonify({'status': 'result recorded'})

@app.route('/scores_history')
def scores_history():
    """Return full match history and leaderboard"""
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    return jsonify({
        "scores": sorted_scores,
        "history": matches_history
    })

@app.route('/stats')
def get_stats():
    """Return aggregate statistics"""
    total = len(matches_history)
    durations = []
    wins = {}

    for m in matches_history:
        if m.get('winner'):
            wins[m['winner']] = wins.get(m['winner'], 0) + 1
        if 'duration' in m:
            durations.append(m['duration'])

    avg_duration = sum(durations) / len(durations) if durations else 0
    win_percentages = {p: (count / total) * 100 for p, count in wins.items()} if total else {}

    return jsonify({
        "total_matches": total,
        "avg_duration": avg_duration,
        "win_percentages": win_percentages
    })

@app.route('/pending_matches')
def pending_matches():
    """List all matches waiting to be joined"""
    return jsonify([
        {
            "code": code,
            "creator": info["creator"],
            "created_at": info["created_at"]
        }
        for code, info in waiting_matches.items()
    ])

@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Unregister a player when their local client shuts down"""
    data = request.json
    username = data.get("username")
    if username in players:
        del players[username]
        print(f"[DISCONNECT] {username} has left the game.")
    return jsonify({'status': 'disconnected'})


# === RUN FLASK ===

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

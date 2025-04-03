from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
from bracket_generator import generate_bracket


app = Flask(__name__)

# === DATA STORES ===

players = {}  # {username: {'ip': ..., 'port': ..., 'joined': ...}}
scores = {}  # {username: score}
matches_history = []  # List of {player1, player2, code, timestamp, winner, duration}
pending_requests = {}  # {to_username: {'from': ..., 'code': ...}}
waiting_matches = {}  # {code: {'creator': username, 'created_at': timestamp}}

tournament_state = {
    "started": False,
    "bracket": None,
    "started_at": None
}


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

@app.route('/start_tournament_match', methods=['POST'])
def start_tournament_match():
    """Lancer un match de tournoi entre deux joueurs"""
    data = request.json
    p1 = data.get("player1")
    p2 = data.get("player2")
    match_id = data.get("match_id")

    if not p1 or not p2 or match_id is None:
        return jsonify({"error": "Missing player names or match ID"}), 400

    # Vérifie que le match existe dans le bracket
    if not tournament_state["bracket"]:
        return jsonify({"error": "No tournament in progress"}), 400

    match = next((m for m in tournament_state["bracket"]["matches"] if m["id"] == match_id), None)
    if not match:
        return jsonify({"error": "Match ID not found in bracket"}), 404

    # Vérifie que le match n'a pas déjà de gagnant
    if match.get("opponent1", {}).get("result") == "win" or match.get("opponent2", {}).get("result") == "win":
        return jsonify({"error": "Match already completed"}), 400

    # Enregistre le match dans l’historique
    match_code = f"{p1}_{p2}_{match_id}"
    matches_history.append({
        "player1": p1,
        "player2": p2,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "winner": None,
        "code": match_code
    })

    return jsonify({"status": "match_started", "code": match_code})

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

# === TOURNAMENT ===

@app.route('/bracket_data')
def dynamic_bracket_data():
    """Return the active bracket or generate one if needed"""
    if tournament_state["started"] and tournament_state["bracket"]:
        return jsonify(tournament_state["bracket"])
    
    current_players = list(players.keys())
    if len(current_players) < 2:
        return jsonify({"error": "Not enough players to start a tournament"}), 400

    return jsonify(generate_bracket(current_players))

@app.route('/start_tournament', methods=['POST'])
def start_tournament():
    """Launch the tournament and store bracket in memory"""
    global tournament_state

    current_players = list(players.keys())
    if len(current_players) < 2:
        return jsonify({"error": "Not enough players"}), 400

    bracket = generate_bracket(current_players)
    tournament_state = {
        "started": True,
        "bracket": bracket,
        "started_at": datetime.now().isoformat()
    }

    print(f"[TOURNAMENT] Started with {len(current_players)} players at {tournament_state['started_at']}")
    return jsonify({"status": "tournament_started", "players": current_players})

@app.route('/tournament_status')
def tournament_status():
    return jsonify({
        "started": tournament_state["started"],
        "started_at": tournament_state["started_at"],
        "player_count": len(players),
        "players": list(players.keys())
    })


@app.route('/reset_tournament', methods=['POST'])
def reset_tournament():
    """Reset the tournament state (admin action)"""
    global tournament_state
    tournament_state = {
        "started": False,
        "bracket": None,
        "started_at": None
    }
    print("[TOURNAMENT] Reset")
    return jsonify({"status": "tournament_reset"})




# === SCORES AND STATS ===
@app.route('/match_result', methods=['POST'])
def match_result():
    """Submit the result of a finished match"""
    data = request.json
    winner = data.get("winner")
    loser = data.get("loser")

    if not winner or not loser:
        return jsonify({'error': 'Missing result data'}), 400

    # ✅ Mise à jour du score général
    scores[winner] = scores.get(winner, 0) + 1

    # ✅ Enregistrement dans l'historique (match le plus récent non terminé)
    for match in reversed(matches_history):
        if match["winner"] is None and winner in [match["player1"], match["player2"]]:
            match["winner"] = winner
            break

    # ✅ Si un tournoi est en cours, on met à jour le bracket
    if tournament_state["started"] and tournament_state["bracket"]:
        matches = tournament_state["bracket"]["matches"]
        current_match = None

        # Trouve le match dans le bracket
        for match in matches:
            if match["opponent1"] and match["opponent1"].get("name") == winner:
                match["opponent1"]["result"] = "win"
                current_match = match
                break
            elif match["opponent2"] and match["opponent2"].get("name") == winner:
                match["opponent2"]["result"] = "win"
                current_match = match
                break

        # Avance automatiquement le gagnant au tour suivant
        if current_match:
            next_round = current_match["round"] + 1
            current_round_matches = [m for m in matches if m["round"] == current_match["round"]]
            next_round_matches = [m for m in matches if m["round"] == next_round]

            # Index du match dans le round courant (permet de savoir où l’envoyer ensuite)
            match_index = current_round_matches.index(current_match)
            next_match_index = match_index // 2

            if next_match_index < len(next_round_matches):
                next_match = next_round_matches[next_match_index]
                target_slot = "opponent1" if not next_match.get("opponent1") else "opponent2"
                next_match[target_slot] = {"id": None, "name": winner}

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
        # Remove any pending requests or matches involving this player
        pending_requests.pop(username, None)
        matches_history[:] = [m for m in matches_history if m["player1"] != username and m["player2"] != username]
        waiting_matches = {k: v for k, v in waiting_matches.items() if v["creator"] != username}
    else:
        print(f"[DISCONNECT] {username} not found in players list.")
    return jsonify({'status': 'disconnected'})


# === RUN FLASK ===

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

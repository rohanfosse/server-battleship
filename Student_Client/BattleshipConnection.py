import socket
import threading
import requests
import json
import time

class BattleshipConnection:
    def __init__(self, username, port, matchmaking_url):
        self.username = username
        self.port = port
        self.matchmaking_url = matchmaking_url
        self.opponent = None
        self.match_code = None
        self.socket = None
        self.is_match_active = False
        self.my_turn = False  # Indicateur pour savoir si c'est le tour du joueur
        self.game_board = {}  # Pour suivre les positions des navires et les tirs
        self.moves = []  # Liste des coups effectués
        self.winner = None

        self.server_ip = None
        self.server_port = None

        # Automatically register with the server
        self.auto_register()

    def auto_register(self):
        """Auto-register the player with the server and get the IP/port of the opponent"""
        try:
            response = requests.post(f"{self.matchmaking_url}/auto_join", json={"username": self.username, "port": self.port})
            data = response.json()
            if response.status_code == 200:
                print(f"[INFO] {self.username} successfully registered.")
                self.server_ip = data["ip"]
                self.server_port = data["port"]
            else:
                print("[ERROR] Could not register with the server.")
        except Exception as e:
            print(f"[ERROR] Failed to connect to server: {e}")

    def propose_match(self, target_username, match_code=None):
        """Propose a match to another player"""
        data = {
            "from": self.username,
            "to": target_username,
            "code": match_code
        }

        try:
            response = requests.post(f"{self.matchmaking_url}/propose_match", json=data)
            if response.status_code == 200:
                print(f"[INFO] Match request sent to {target_username}.")
                return True
            else:
                print(f"[ERROR] Failed to send match request to {target_username}.")
                return False
        except Exception as e:
            print(f"[ERROR] Error sending match request: {e}")
            return False

    def join_match(self, match_code):
        """Join a match with the provided code"""
        try:
            response = requests.post(f"{self.matchmaking_url}/join_match", json={"player_id": self.username, "code": match_code})
            if response.status_code == 200:
                data = response.json()
                self.opponent = data['players'][1] if data['players'][0] == self.username else data['players'][0]
                print(f"[INFO] Joined match with code {match_code}. Playing against {self.opponent}.")
                self.match_code = match_code
                self.is_match_active = True
                self.my_turn = True  # Player 1 always starts first
                return True
            else:
                print("[ERROR] Failed to join the match.")
                return False
        except Exception as e:
            print(f"[ERROR] Error joining match: {e}")
            return False

    def start_socket_listener(self):
        """Start listening for game messages from the opponent"""
        s = socket.socket()
        s.bind(("0.0.0.0", self.port))
        s.listen(1)

        print(f"[INFO] Listening on port {self.port} for game moves...")

        while self.is_match_active:
            conn, addr = s.accept()
            data = conn.recv(1024).decode()
            if data:
                print(f"[INFO] Received message: {data}")
                self.handle_opponent_move(data)
            conn.close()

    def send_move(self, move):
        """Send a move to the opponent"""
        if not self.socket:
            print("[ERROR] No connection to opponent.")
            return

        message = json.dumps({"move": move})
        try:
            self.socket.send(message.encode())
            print(f"[INFO] Sent move: {move}")
        except Exception as e:
            print(f"[ERROR] Failed to send move: {e}")

    def handle_opponent_move(self, data):
        """Handle the opponent's move"""
        try:
            move = json.loads(data)["move"]
            print(f"[INFO] Opponent's move: {move}")
            # Handle the opponent's move here (game logic)
            self.update_game_board(move, opponent=True)
        except Exception as e:
            print(f"[ERROR] Error parsing opponent's move: {e}")

    def update_game_board(self, move, opponent=False):
        """Update the game board with the given move"""
        if opponent:
            self.game_board[move] = "HIT" if self.game_board.get(move) == "SHIP" else "MISS"
            print(f"Opponent's move: {move} -> {self.game_board[move]}")
        else:
            self.game_board[move] = "SHIP"
            print(f"Your move: {move} -> Placed a ship at {move}")
        
        self.moves.append(move)
        self.check_victory()

    def check_victory(self):
        """Check if the current player has won"""
        if len(self.game_board) >= 5:  # Victory condition (arbitrary, adjust as needed)
            self.winner = self.username
            self.end_game()

    def start_game(self):
        """Start the game after both players agree"""
        print(f"[INFO] Game started with {self.opponent}.")
        # Now that the match has started, start the socket listener in a separate thread
        listener_thread = threading.Thread(target=self.start_socket_listener)
        listener_thread.daemon = True
        listener_thread.start()

    def end_game(self):
        """End the game and record the result"""
        try:
            response = requests.post(f"{self.matchmaking_url}/match_result", json={"winner": self.winner, "loser": self.opponent})
            if response.status_code == 200:
                print(f"[INFO] Game result recorded. {self.winner} wins!")
            else:
                print("[ERROR] Failed to record match result.")
        except Exception as e:
            print(f"[ERROR] Error ending game: {e}")

import random
import socket
import threading
import requests
import json
import time
from Student_Client.core.BattleshipConnection import BattleshipConnection

# === CONFIGURATION ===
with open("config.json") as f:
    config = json.load(f)

USERNAME = config["username"]
PORT = config["port"]
SERVER_URL = config["matchmaking_url"]
MATCH_CODE = config.get("match_code", "MATCH_AI")

# === Connexion au serveur de matchmaking ===
conn = BattleshipConnection(USERNAME, PORT, SERVER_URL)

# === CLASSE IA INTELLIGENTE ===
class SmartAI:
    def __init__(self):
        self.pos_visited = set()
        self.pos_to_try = [(x, y) for x in range(5) for y in range(5)]
        random.shuffle(self.pos_to_try)
        self.last_hits = []

    def choose_next_move(self):
        if self.last_hits:
            neighbors = self.get_neighbors(self.last_hits[-1])
            for n in neighbors:
                if n not in self.pos_visited:
                    return n
        for move in self.pos_to_try:
            if move not in self.pos_visited:
                return move
        return None

    def get_neighbors(self, pos):
        x, y = pos
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        return [(x+dx, y+dy) for dx, dy in directions if 0 <= x+dx < 5 and 0 <= y+dy < 5]

    def mark_result(self, move, result):
        self.pos_visited.add(move)
        if result == "HIT":
            self.last_hits.append(move)

ai = SmartAI()

# === PLACEMENT DES NAVIRES AUTOMATIQUE ===
def auto_place_ships():
    print("🚢 Placement automatique de 3 navires...")
    ships = set()
    while len(ships) < 3:
        ships.add((random.randint(0, 4), random.randint(0, 4)))
    for pos in ships:
        conn.update_game_board(pos, opponent=False)
    print("✅ Navires placés :", ships)

# === ENVOI D’UN COUP À L’ADVERSAIRE ===
def envoyer_coup(move):
    if not conn.opponent:
        print("⚠️ Aucun adversaire connu.")
        return
    try:
        r = requests.get(f"{SERVER_URL}/players")
        players = r.json()
        target = next((p for p in players if p["username"] == conn.opponent), None)
        if not target:
            print("❌ Adversaire introuvable.")
            return
        ip, port = target["ip"], target["port"]
        s = socket.socket()
        s.connect((ip, port))
        s.send(json.dumps({"move": list(move)}).encode())
        s.close()
        print(f"🚀 Coup envoyé vers {move}")
    except Exception as e:
        print("❌ Erreur lors de l'envoi :", e)

# === MATCHMAKING ===
def rejoindre_ou_creer_match():
    success = conn.join_match(MATCH_CODE)
    if not success:
        adversaire = input("🎯 Nom de l’adversaire pour créer un match : ").strip()
        success = conn.propose_match(adversaire, MATCH_CODE)
        if success:
            print("🕒 Attente de confirmation...")
            time.sleep(5)

# === BOUCLE DE JEU PRINCIPALE ===
def boucle_de_jeu():
    while conn.is_match_active and not conn.winner:
        time.sleep(1)
        if conn.my_turn:
            move = ai.choose_next_move()
            if move:
                envoyer_coup(move)
                conn.my_turn = False

# === LISTENER CUSTOM : gère les coups reçus + maj IA ===
def start_game_with_ai():
    def custom_handle(data):
        try:
            move = tuple(json.loads(data)["move"])
            print(f"📥 Coup reçu : {move}")
            result = "MISS"
            if conn.game_board.get(move) == "SHIP":
                conn.game_board[move] = "HIT"
                result = "HIT"
                print(f"💥 Touché en {move}")
            else:
                conn.game_board[move] = "MISS"
            ai.mark_result(move, result)
            conn.moves.append(move)
            conn.check_victory()
        except Exception as e:
            print("❌ Erreur gestion du coup :", e)

    conn.handle_opponent_move = custom_handle
    conn.start_game()

# === EXECUTION ===
if __name__ == "__main__":
    print(f"🤖 Démarrage IA '{USERNAME}' sur le port {PORT}")
    rejoindre_ou_creer_match()
    if conn.is_match_active:
        auto_place_ships()
        start_game_with_ai()
        boucle_de_jeu()
        print("🏁 Fin du match")
        if conn.winner:
            print(f"🏆 Gagnant : {conn.winner}")
        else:
            print("😶 Match nul")

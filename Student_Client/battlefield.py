import json
import threading
from BattleshipConnection import BattleshipConnection

# === CONFIGURATION ===
with open("config.json") as f:
    config = json.load(f)

USERNAME = config["username"]
PORT = config["port"]
SERVER_URL = config["matchmaking_url"]
MATCH_CODE = input("💬 Entrez le code de match à utiliser (ex: ABC123) : ").strip()

# === INIT ===
conn = BattleshipConnection(USERNAME, PORT, SERVER_URL)

# === AFFICHAGE ===
def afficher_grille(grille):
    print("   " + " ".join([str(i) for i in range(5)]))
    for y in range(5):
        row = [grille.get(f"{x},{y}", ".") for x in range(5)]
        print(f"{y}  " + " ".join(row))
    print()

# === POSITIONNEMENT DES NAVIRES ===
def positionner_navires():
    print("🛠 Placez 3 navires sur une grille 5x5 (ex: 0,0)")
    for i in range(3):
        while True:
            pos = input(f"Navire {i+1}/3 ➤ Position : ").strip()
            if pos in conn.game_board:
                print("❌ Déjà placé.")
                continue
            x, y = map(int, pos.split(","))
            if 0 <= x < 5 and 0 <= y < 5:
                conn.update_game_board(pos, opponent=False)
                break
            else:
                print("⚠️ Coordonnées invalides.")
    print("✅ Navires placés.")

# === BOUCLE DE JEU ===
def tour_de_jeu():
    while conn.is_match_active:
        print("\n🎯 Plateau actuel :")
        afficher_grille(conn.game_board)

        if conn.my_turn:
            move = input("🔥 Votre coup (ex: 2,3) : ").strip()
            conn.send_move(move)
            conn.my_turn = False
        else:
            print("⏳ En attente du coup de l'adversaire...")
            threading.Event().wait(2)  # Petite pause d'attente

# === EXECUTION ===
if __name__ == "__main__":
    print(f"👤 {USERNAME} se connecte au serveur...")

    # Rejoindre ou créer un match
    success = conn.join_match(MATCH_CODE)
    if not success:
        success = conn.propose_match(input("➕ Nom de l'adversaire : "), MATCH_CODE)
        if success:
            print("🕒 En attente de confirmation...")
            threading.Event().wait(5)

    if conn.is_match_active:
        positionner_navires()
        conn.start_game()
        tour_de_jeu()

import threading
import socket
import json
import time
import random
from Student_Client.core.BattleshipConnection import BattleshipConnection

# === CONFIGURATION ===
PLAYER1 = {"username": "Alice", "port": 9001}
PLAYER2 = {"username": "Bob", "port": 9002}
SERVER_URL = "http://localhost:5000"

# === OUTILS ===

def print_board(board, title):
    print(f"\n{title}")
    print("  A B C D E")
    for y in range(5):
        row = f"{y+1} "
        for x in range(5):
            cell = board.get((x, y), ".")
            row += f"{cell[0] if cell != '.' else '.'} "
        print(row)
    print()

def send_message(ip, port, move):
    s = socket.socket()
    s.connect((ip, port))
    s.send(json.dumps({"move": tuple(move)}).encode())
    s.close()

def random_coordinates(count):
    return random.sample([(x, y) for x in range(5) for y in range(5)], count)

# === LOGIQUE DU JOUEUR ===

def run_player(conn, ships):
    conn.game_board = {coord: "SHIP" for coord in ships}
    conn.is_match_active = True
    conn.start_game()

# === SIMULATION ===

def simulate_game(player1, player2):
    # Initialisation des connexions
    conn1 = BattleshipConnection(player1["username"], player1["port"], SERVER_URL)
    time.sleep(1)
    conn2 = BattleshipConnection(player2["username"], player2["port"], SERVER_URL)

    match_code = "MATCH42"
    conn1.propose_match(player2["username"], match_code)
    time.sleep(1)
    conn2.join_match(match_code)

    # Placement des navires aléatoires
    ships1 = random_coordinates(3)
    ships2 = random_coordinates(3)

    # Lancement des threads d'écoute
    threading.Thread(target=run_player, args=(conn1, ships1), daemon=True).start()
    threading.Thread(target=run_player, args=(conn2, ships2), daemon=True).start()
    time.sleep(2)

    # Coups aléatoires pour chaque joueur
    moves1 = random_coordinates(10)
    moves2 = random_coordinates(10)

    # Boucle de jeu
    for i in range(10):
        if conn1.winner or conn2.winner:
            break

        move1 = moves1[i]
        move2 = moves2[i]

        print(f"[{player1['username']}] Tire en {move1}")
        send_message("127.0.0.1", player2["port"], move1)
        time.sleep(1)

        print(f"[{player2['username']}] Tire en {move2}")
        send_message("127.0.0.1", player1["port"], move2)
        time.sleep(1)

        print_board(conn1.game_board, f"{player1['username']} (défense)")
        print_board(conn2.game_board, f"{player2['username']} (défense)")

    # Résultat
    print("\n🎉 Fin de la partie !")
    if conn1.winner:
        print(f"🏆 {conn1.winner} a gagné !")
    elif conn2.winner:
        print(f"🏆 {conn2.winner} a gagné !")
    else:
        print("😅 Match nul ou aucune victoire atteinte.")

# === LANCEMENT ===
if __name__ == "__main__":
    simulate_game(PLAYER1, PLAYER2)

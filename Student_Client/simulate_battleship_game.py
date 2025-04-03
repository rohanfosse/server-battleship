import threading
import socket
import json
import time
from BattleshipConnection import BattleshipConnection

# === CONFIGURATION ===
PLAYER1 = {"username": "Alice", "port": 9001}
PLAYER2 = {"username": "Bob", "port": 9002}
SERVER_URL = "http://localhost:5000"

# === UTILS ===

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

def coordinates(letter, number):
    x = "ABCDE".index(letter.upper())
    y = int(number) - 1
    return (x, y)

def send_message(ip, port, move):
    s = socket.socket()
    s.connect((ip, port))
    s.send(json.dumps({"move": move}).encode())
    s.close()

# === GAME SIMULATION ===

def run_player(conn, ships):
    conn.game_board = {coord: "SHIP" for coord in ships}
    conn.is_match_active = True
    conn.start_game()

def simulate_game(player1, player2):
    # Initialisation
    conn1 = BattleshipConnection(player1["username"], player1["port"], SERVER_URL)
    time.sleep(1)  # Attendre que le serveur soit prêt
    conn2 = BattleshipConnection(player2["username"], player2["port"], SERVER_URL)

    match_code = "MATCH42"
    conn1.propose_match(player2["username"], match_code)
    time.sleep(1)
    conn2.join_match(match_code)

    # Placement des navires (3 par joueur)
    ships1 = [(0, 0), (1, 1), (2, 2)]
    ships2 = [(4, 0), (3, 1), (2, 3)]

    # Démarrage des listeners
    threading.Thread(target=run_player, args=(conn1, ships1), daemon=True).start()
    threading.Thread(target=run_player, args=(conn2, ships2), daemon=True).start()

    time.sleep(2)

    moves1 = [(4, 0), (3, 1), (2, 3), (0, 4)]
    moves2 = [(0, 0), (1, 1), (2, 2), (4, 4)]

    i = 0
    while conn1.winner is None and conn2.winner is None and i < 10:
        # P1 tire
        move = moves1[i % len(moves1)]
        print(f"[{player1['username']}] Tire en {move}")
        send_message("127.0.0.1", player2["port"], move)
        time.sleep(1)

        # P2 tire
        move = moves2[i % len(moves2)]
        print(f"[{player2['username']}] Tire en {move}")
        send_message("127.0.0.1", player1["port"], move)
        time.sleep(1)

        print_board(conn1.game_board, f"{player1['username']} (def)")
        print_board(conn2.game_board, f"{player2['username']} (def)")

        i += 1

    print("\n🎉 Fin de la partie !")
    if conn1.winner:
        print(f"🏆 {conn1.winner} a gagné !")
    elif conn2.winner:
        print(f"🏆 {conn2.winner} a gagné !")
    else:
        print("😅 Match nul ou erreur de logique.")


# === LANCEMENT ===
if __name__ == "__main__":
    simulate_game(PLAYER1, PLAYER2)

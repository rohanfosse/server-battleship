import pygame
import sys
import threading
import json
import requests
import socket
import time
from Student_Client.core.BattleshipConnection import BattleshipConnection

# === CONFIGURATION ===
with open("config.json") as f:
    config = json.load(f)

USERNAME = config["username"]
PORT = config["port"]
SERVER_URL = config["matchmaking_url"]
MATCH_CODE = input("💬 Entrez le code de match à utiliser (ex: ABC123) : ").strip()

# === INITIALISATION DE LA CONNEXION ===
conn = BattleshipConnection(USERNAME, PORT, SERVER_URL)

# === PARAMÈTRES PYGAME ===
GRID_SIZE = 5
CELL_SIZE = 80
MARGIN = 50
WIDTH = GRID_SIZE * CELL_SIZE + MARGIN * 2
HEIGHT = GRID_SIZE * CELL_SIZE * 2 + MARGIN * 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
GRAY = (200, 200, 200)
GREEN = (34, 139, 34)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"🎯 Battleship - {USERNAME}")
font = pygame.font.SysFont("consolas", 20)

# === OUTILS ===
def get_cell_from_pos(pos, top_offset):
    x, y = pos
    grid_x = (x - MARGIN) // CELL_SIZE
    grid_y = (y - top_offset) // CELL_SIZE
    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
        return (grid_x, grid_y)
    return None

def draw_board(board, top_offset, title):
    pygame.draw.rect(screen, WHITE, (0, top_offset - 40, WIDTH, GRID_SIZE * CELL_SIZE + 40))
    label = font.render(title, True, BLACK)
    screen.blit(label, (MARGIN, top_offset - 30))

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(MARGIN + x * CELL_SIZE, top_offset + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

            val = board.get((x, y), ".")
            if val == "SHIP":
                pygame.draw.rect(screen, BLUE, rect.inflate(-4, -4))
            elif val == "HIT":
                pygame.draw.rect(screen, RED, rect.inflate(-4, -4))
            elif val == "MISS":
                pygame.draw.rect(screen, GRAY, rect.inflate(-4, -4))

def envoyer_coup(move):
    try:
        r = requests.get(f"{SERVER_URL}/players")
        if r.status_code == 200:
            players = r.json()
            opponent_info = next((p for p in players if p["username"] == conn.opponent), None)
            if opponent_info:
                ip = opponent_info["ip"]
                port = opponent_info["port"]
                s = socket.socket()
                s.connect((ip, port))
                s.send(json.dumps({"move": list(move)}).encode())  # list() car JSON n’aime pas les tuples
                s.close()
                print(f"🧨 Coup envoyé en {move}")
            else:
                print("⚠️ Adversaire non trouvé sur le serveur.")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du coup : {e}")

def game_loop():
    placing = True
    ships_placed = 0
    opponent_board = {}

    while True:
        screen.fill(WHITE)
        draw_board(conn.game_board, MARGIN, f"🛡 Votre plateau ({USERNAME})")
        draw_board(opponent_board, HEIGHT // 2 + MARGIN // 2, f"🎯 Plateau adverse ({conn.opponent or 'inconnu'})")
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if placing:
                    cell = get_cell_from_pos(pos, MARGIN)
                    if cell and conn.game_board.get(cell) != "SHIP":
                        conn.update_game_board(cell, opponent=False)
                        ships_placed += 1
                        if ships_placed == 3:
                            placing = False
                            conn.start_game()
                elif conn.my_turn and not conn.winner:
                    cell = get_cell_from_pos(pos, HEIGHT // 2 + MARGIN // 2)
                    if cell:
                        envoyer_coup(cell)
                        conn.my_turn = False

        if conn.winner:
            screen.fill(WHITE)
            msg = f"🏆 {conn.winner} a gagné !"
            label = font.render(msg, True, GREEN)
            screen.blit(label, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(5000)
            pygame.quit()
            sys.exit()

# === MATCHMAKING ===
print(f"👤 Connexion au serveur...")
if not conn.join_match(MATCH_CODE):
    opponent = input("➕ Nom de l'adversaire : ")
    if conn.propose_match(opponent, MATCH_CODE):
        print("⏳ En attente de l'adversaire...")
        time.sleep(5)

if conn.is_match_active:
    game_loop()
else:
    print("❌ Impossible de lancer le match.")

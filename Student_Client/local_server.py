import socket
import threading
import requests
import json
import time
import atexit
import argparse

# === Chargement de la configuration initiale ===
with open("config.json") as f:
    config = json.load(f)

DEFAULT_PORT = config["port"]
SERVER_URL = config["matchmaking_url"]
USERNAME = None
REGISTERED = False

# === Parser de ligne de commande pour override le port ===
parser = argparse.ArgumentParser(description="Client local Battleship")
parser.add_argument("--port", type=int, help="Port local à utiliser (optionnel)")
args = parser.parse_args()

PORT = args.port if args.port else DEFAULT_PORT

def get_public_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        print(f"🌍 Adresse IP publique : {ip}")
    except:
        print("⚠️ Impossible de déterminer l'adresse IP publique.")

def auto_register():
    global REGISTERED
    try:
        r = requests.post(f"{SERVER_URL}/auto_join", json={
            "username": USERNAME,
            "port": PORT
        })
        if r.status_code == 200:
            print(f"✅ Enregistré en tant que '{USERNAME}' sur le serveur")
            REGISTERED = True
        else:
            print("❌ Échec de l'enregistrement :", r.text)
    except Exception as e:
        print("❌ Impossible de joindre le serveur :", e)

def handle_match_request(message):
    parts = message.strip().split(":")
    if parts[0] != "MATCH_REQUEST":
        print("⚠️ Format de message inconnu :", message)
        return

    challenger = parts[1]
    code = parts[2] if len(parts) > 2 else None

    print(f"\n🔔 Demande de match de {challenger} (code : {code or 'aucun'})")
    response = input("Acceptez-vous le match ? (oui/non) : ").strip().lower()

    if response == "oui":
        try:
            r = requests.post(f"{SERVER_URL}/confirm_match", json={
                "player1": challenger,
                "player2": USERNAME,
                "code": code
            })
            if r.status_code == 200:
                print("✅ Match accepté.")
            else:
                print("⚠️ Impossible de confirmer le match :", r.text)
        except Exception as e:
            print("❌ Échec de la confirmation du match :", e)
    else:
        print("❌ Match refusé.")

def socket_listener():
    s = socket.socket()
    s.bind(("0.0.0.0", PORT))
    s.listen()
    print(f"🔌 En écoute pour les demandes de match sur le port {PORT}...")

    while True:
        conn, addr = s.accept()
        data = conn.recv(1024).decode()
        if data:
            handle_match_request(data)
        conn.close()

def match_result():
    gagnant = input("Entrez le nom d'utilisateur du gagnant : ").strip()
    perdant = input("Entrez le nom d'utilisateur du perdant : ").strip()

    try:
        r = requests.post(f"{SERVER_URL}/match_result", json={
            "winner": gagnant,
            "loser": perdant
        })
        if r.status_code == 200:
            print("🏆 Résultat du match soumis avec succès.")
        else:
            print("⚠️ Échec de la soumission du résultat :", r.text)
    except Exception as e:
        print("❌ Impossible de soumettre le résultat du match :", e)

def create_match():
    code = input("Entrez un code de match (par exemple, ABC123) : ").strip()
    if not code:
        print("⚠️ Code requis.")
        return
    try:
        r = requests.post(f"{SERVER_URL}/create_match", json={
            "player_id": USERNAME,
            "code": code
        })
        if r.status_code == 200:
            print(f"📡 En attente qu'un adversaire rejoigne le match '{code}'...")
            while True:
                status = requests.get(f"{SERVER_URL}/match_status", params={"code": code})
                if status.status_code == 200:
                    data = status.json()
                    if data.get("status") == "active":
                        print(f"🎮 Match '{code}' commencé avec {data.get('opponent')}.")
                        break
                time.sleep(5)
        else:
            print("⚠️ Impossible de créer le match :", r.text)
    except Exception as e:
        print("❌ Échec de la création du match :", e)

def join_match():
    code = input("Entrez le code du match à rejoindre : ").strip()
    if not code:
        print("⚠️ Code requis.")
        return
    try:
        r = requests.post(f"{SERVER_URL}/join_match", json={
            "player_id": USERNAME,
            "code": code
        })
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Rejoint le match : {data.get('players')}")
        else:
            print("⚠️ Impossible de rejoindre le match :", r.text)
    except Exception as e:
        print("❌ Échec de la jonction au match :", e)

def cleanup():
    try:
        requests.post(f"{SERVER_URL}/disconnect", json={"username": USERNAME})
        print("🚪 Déconnecté proprement du serveur.")
    except Exception as e:
        print("⚠️ Impossible de notifier le serveur :", e)

atexit.register(cleanup)

def main_menu():
    while True:
        print("\n🎮 Commandes disponibles :")
        print("1. Créer un match")
        print("2. Rejoindre un match")
        print("3. Soumettre le résultat d'un match")
        print("4. Quitter")
        choix = input("Choisissez une action [1-4] : ").strip()

        if choix == "1":
            create_match()
        elif choix == "2":
            join_match()
        elif choix == "3":
            match_result()
        elif choix == "4":
            print("👋 Fermeture du client.")
            break
        else:
            print("❌ Choix invalide.")

# === DÉMARRAGE ===
if __name__ == "__main__":
    print("🎮 Démarrage du client Battleship local...")
    get_public_ip()

    USERNAME = input("Entrez votre nom d'utilisateur : ").strip()
    if not USERNAME:
        print("❌ Nom d'utilisateur requis. Fermeture.")
        exit(1)

    threading.Thread(target=auto_register).start()
    threading.Thread(target=socket_listener, daemon=True).start()
    main_menu()

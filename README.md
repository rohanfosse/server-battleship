# **README - Intégration et Gestion des Mouvements de Jeu pour Battleship**

## **Introduction**

Dans ce projet, les étudiants joueront à **Battleship** en utilisant un serveur de matchmaking en ligne et un serveur local pour faciliter les connexions et les échanges entre joueurs. Ce guide vous permettra de configurer correctement votre client de jeu et de gérer les mouvements de jeu entre les deux joueurs.

### **Objectifs**

- Vérifier la connexion entre le client et le serveur de matchmaking.
- Gérer l'envoi et la réception des mouvements de jeu.
- Soumettre les résultats des parties lorsque celles-ci sont terminées.

## **Fichiers et Configuration**

### **1. Fichier de configuration (`config.json`)**

Le fichier **`config.json`** contient les informations nécessaires à la connexion au serveur de matchmaking et au serveur local. Il doit être configuré comme suit :

```json
{
    "username": "NomUtilisateur", 
    "port": 5555, 
    "matchmaking_url": "https://rfosse.pythonanywhere.com"
}
```

- **`username`** : Nom d'utilisateur unique du joueur.
- **`port`** : Le port sur lequel le client écoutera les connexions.
- **`matchmaking_url`** : L'URL du serveur de matchmaking en ligne.

### **2. Fichier `local_server.py`**

Le fichier **`local_server.py`** gère la connexion locale, l'enregistrement du joueur et les demandes de match. Voici une brève explication des fonctions importantes :

#### **a. Enregistrement automatique**

Lorsque le client démarre, le joueur est automatiquement enregistré sur le serveur de matchmaking via la méthode `auto_register()` :

```python
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
```

#### **b. Créer ou rejoindre un match**

- **Créer un match** : Un joueur peut créer un match avec un code de match unique via la méthode `create_match()` :

```python
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
            # Attente qu'un autre joueur rejoigne le match
            while True:
                status = requests.get(f"{SERVER_URL}/match_status", params={"code": code})
                if status.status_code == 200:
                    data = status.json()
                    if data.get("status") == "active":
                        print(f"🎮 Match '{code}' commencé avec {data.get('opponent')}.")
                        break
                time.sleep(5)  # Vérification toutes les 5 secondes
        else:
            print("⚠️ Impossible de créer le match :", r.text)
    except Exception as e:
        print("❌ Échec de la création du match :", e)
```

- **Rejoindre un match** : Un joueur peut rejoindre un match existant en utilisant le code du match :

```python
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
```

#### **c. Écouter les demandes de match**

Le serveur local écoute en permanence les demandes de match en attente. Lorsqu'une demande est reçue, il demande à l'utilisateur s'il souhaite accepter ou refuser la demande via la méthode `handle_match_request()` :

```python
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
```

### **3. Gestion des Mouvements de Jeu**

Une fois le match lancé, vous devez gérer les mouvements de jeu entre les joueurs.

#### **Envoyer un Mouvement**

Chaque joueur peut envoyer un mouvement (par exemple, viser une case) à l'adversaire. Vous pouvez envoyer un mouvement avec la méthode `send_move()` :

```python
def send_move(self, move):
    """Envoie un mouvement à l'adversaire"""
    if not self.socket:
        print("[ERROR] No connection to opponent.")
        return

    message = json.dumps({"move": move})
    try:
        self.socket.send(message.encode())
        print(f"[INFO] Sent move: {move}")
    except Exception as e:
        print(f"[ERROR] Failed to send move: {e}")
```

#### **Recevoir un Mouvement**

Le serveur écoute en continu les mouvements envoyés par l'adversaire via un socket. Lorsque le mouvement est reçu, il est traité et appliqué sur le tableau de jeu avec la méthode `handle_opponent_move()` :

```python
def handle_opponent_move(self, data):
    """Traite le mouvement de l'adversaire"""
    try:
        move = json.loads(data)["move"]
        print(f"[INFO] Mouvement de l'adversaire : {move}")
        # Appliquer la logique de jeu ici pour mettre à jour le tableau de jeu
        self.update_game_board(move, opponent=True)
    except Exception as e:
        print(f"[ERROR] Erreur lors du traitement du mouvement de l'adversaire : {e}")
```

### **4. Vérification de la Victoire et Soumission des Résultats**

Lorsque le jeu est terminé, vous pouvez vérifier la victoire avec `check_victory()` et soumettre les résultats avec `end_game()` :

```python
def check_victory(self):
    """Vérifie si un joueur a gagné"""
    if len(self.game_board) >= 5:  # Condition de victoire (ajustez selon votre logique)
        self.winner = self.username
        self.end_game()

def end_game(self):
    """Enregistre le résultat du match"""
    try:
        response = requests.post(f"{self.matchmaking_url}/match_result", json={"winner": self.winner, "loser": self.opponent})
        if response.status_code == 200:
            print(f"[INFO] Résultat du match enregistré. {self.winner} gagne!")
        else:
            print("[ERROR] Impossible d'enregistrer le résultat du match.")
    except Exception as e:
        print(f"[ERROR] Erreur lors de la fin du match : {e}")
```

## **5. Test et Validation**

1. **Démarrer le serveur local** : Lancer le serveur local (`local_server.py`) pour gérer les connexions.
2. **Lancer le client de jeu** : Connecter votre client graphique de jeu en utilisant `BattleshipConnection`.
3. **Tester la connexion** : Assurez-vous que l'enregistrement et la connexion au serveur de matchmaking fonctionnent correctement.
4. **Tester les mouvements** : Testez l'envoi et la réception des mouvements de jeu entre deux joueurs.
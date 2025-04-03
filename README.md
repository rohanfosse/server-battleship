# ⚙️ **Classe `BattleshipConnection` — Vue d’ensemble**

Cette classe représente un joueur connecté à un **serveur de matchmaking**. Elle permet :

- de s’inscrire sur le serveur
- de créer ou rejoindre un match
- d’écouter les messages de l’adversaire via un socket
- d’envoyer et recevoir des coups
- de détecter et enregistrer la fin de partie

---

## 🔌 Connexion au serveur de matchmaking

### `__init__(self, username, port, matchmaking_url)`
- Initialise les données du joueur (nom, port, URL du serveur)
- Lance l’enregistrement automatique (`auto_register()`)

---

### `auto_register(self)`
> Permet d’enregistrer le joueur auprès du serveur Flask

- Envoie `username` et `port` au serveur (`/auto_join`)
- Réponse attendue : `{"status": "connected"}`

**Important :** permet au serveur de savoir sur quelle IP/port envoyer les demandes de match.

---

## 🎮 Matchmaking

### `propose_match(self, target_username, match_code=None)`
> Permet d’envoyer une demande de match à un autre joueur.

- Appelle `/propose_match` avec : nom du joueur courant, cible, et code de match.
- Si ça marche, l’adversaire sera notifié via son serveur local.

---

### `join_match(self, match_code)`
> Rejoint un match existant avec un `code`.

- Appelle `/join_match` côté serveur
- Enregistre l’adversaire (`self.opponent`)
- Active le jeu (`self.is_match_active = True`)
- Le joueur 2 prend la main (`self.my_turn = True`)

---

## 🔁 Écoute réseau

### `start_socket_listener(self)`
> Écoute en **permanence** les coups reçus via socket local.

- Ouvre un socket TCP sur le port du joueur (`self.port`)
- Lorsqu’une connexion est reçue, lit le message JSON et appelle `handle_opponent_move()`

Ex. de message reçu :
```json
{"move": [2, 3]}
```

---

## 💥 Échanges de coups

### `send_move(self, move)`
> Envoie un coup (ex: `(2, 3)`) à l’adversaire via socket.

> ⚠️ La variable `self.socket` n’est pas utilisée dans la dernière logique !  
Tu peux soit :
- modifier la méthode pour envoyer via IP/port comme `send_message(ip, port, move)`
- ou garder `self.socket` uniquement si une connexion directe est établie (rare ici)

---

### `handle_opponent_move(self, data)`
> Décode et traite un coup reçu.

- Décode le JSON (`move = tuple(json.loads(data)["move"])`)
- Appelle `update_game_board(move, opponent=True)`

---

### `update_game_board(self, move, opponent=False)`
> Met à jour le plateau de jeu (`self.game_board`) après un coup.

- Si `opponent=True`, regarde si la case touchée contenait un navire :
  - `SHIP` → devient `HIT`
  - sinon → `MISS`
- Ajoute le coup à `self.moves`
- Appelle `check_victory()` pour voir si le jeu est terminé

---

## 🏆 Fin de partie

### `check_victory(self)`
> Vérifie si l’adversaire a réussi à couler 3 de tes navires.

```python
enemy_hits = [v for v in self.game_board.values() if v == "HIT"]
if len(enemy_hits) >= 3:
    self.winner = self.opponent
    self.end_game()
```

---

### `end_game(self)`
> Enregistre le résultat final de la partie via le serveur.

- Envoie une requête à `/match_result` avec `winner` et `loser`
- Le serveur met à jour le bracket ou l’historique

```python
requests.post(f"{self.matchmaking_url}/match_result", {
    "winner": self.winner,
    "loser": loser
})
```


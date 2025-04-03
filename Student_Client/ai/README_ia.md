# 🤖 README – Battleship AI Player

## 🎯 Objectif

Ce document explique comment utiliser le **joueur automatique IA** dans le projet **Battleship**, capable de :
- Se connecter au serveur de matchmaking
- Rejoindre un match ou en créer un
- Placer automatiquement ses navires
- Jouer contre un joueur **humain en ligne** via sockets
- **Prendre des décisions intelligentes** pour ses coups

---

## 📁 Fichier principal

Le fichier utilisé pour l’IA est :  
**`battleship_ai.py`**

---

## 🔧 Prérequis

1. **Python 3.8+**
2. Serveur Flask déjà lancé (`server.py`)
3. Un autre joueur (humain) en ligne ou sur le même réseau

---

## ⚙️ `config.json` – Configuration

Avant de lancer le fichier, assurez-vous que votre `config.json` est bien configuré :

```json
{
  "username": "AI_Bot",
  "port": 9001,
  "matchmaking_url": "http://localhost:5000",
  "match_code": "MATCH42"
}
```

- `username`: Nom d'utilisateur unique pour l'IA
- `port`: Port sur lequel l'IA écoutera les coups entrants
- `matchmaking_url`: Adresse du serveur Flask
- `match_code`: Code partagé avec l'adversaire

---

## 🚀 Lancement de l’IA

Ouvrez un terminal et lancez le script :

```bash
python battleship_ai.py
```

---

## 🧠 Fonctionnement de l'IA

L'IA :

- S’enregistre automatiquement sur le serveur
- Rejoint un match avec un `match_code`
- Place **3 navires aléatoirement**
- Joue en priorité autour des coups réussis (stratégie intelligente)
- Écoute les attaques de l’adversaire via un **socket local**
- Marque les coups reçus et s’arrête quand le match est terminé

---

## 🎮 Match contre un joueur humain

Pour affronter l’IA, un joueur humain doit :

1. Lancer son propre `local_server.py`
2. Rejoindre le **même `match_code`** que celui utilisé par l’IA
3. Jouer normalement via l’interface console ou PyGame

---

## 🔄 Exemple d’interaction

```bash
🤖 Démarrage IA 'AI_Bot' sur le port 9001
🎯 Nom de l’adversaire pour créer un match : Rohan
🕒 Attente de confirmation...
🚢 Placement automatique de 3 navires...
✅ Navires placés : {(0, 0), (1, 2), (3, 4)}
🚀 Coup envoyé vers (1, 1)
📥 Coup reçu : (3, 4)
💥 Touché en (3, 4)
...
🏁 Fin du match
🏆 Gagnant : Rohan
```

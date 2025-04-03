// player.js

/**
 * Placeholder for future player profile logic.
 * You can load player stats, display match history, etc.
 */

function loadPlayerProfile(username = "Alice") {
    fetch(`/player_profile/${username}`)
      .then(res => res.json())
      .then(player => {
        document.getElementById("player-name").innerText = player.name;
        document.getElementById("player-wins").innerText = player.wins;
        document.getElementById("player-losses").innerText = player.losses;
        document.getElementById("player-time").innerText = player.avgTime;
  
        const historyList = document.getElementById("player-history");
        historyList.innerHTML = player.history.map(h => `
          <li class="list-group-item">${player.name} vs ${h.opponent} ➜ ${h.result}</li>
        `).join('');
      });
  }
  
// tournament.js

let bracketViewer = null;

/**
 * Fetches and renders the bracket from the server (/bracket_data).
 */
function generateBracket() {
  fetch("/bracket_data")
    .then(async res => {
      const text = await res.text();
      try {
        return JSON.parse(text);
      } catch (e) {
        console.error("Invalid JSON from /bracket_data:", text);
        throw new Error("Invalid JSON returned by server.");
      }
    })
    .then(data => {
      if (data.error) {
        alert("Error: " + data.error);
        console.warn("Bracket error:", data.error);
        return;
      }

      if (!data.stages || !data.matches || !data.participants) {
        alert("Invalid bracket data structure.");
        console.error("Bracket data missing required fields:", data);
        return;
      }

      // Clear previous content
      const viewerContainer = document.getElementById("bracket-viewer");
      viewerContainer.innerHTML = "";

      // Render bracket manually
      renderNativeBracket(viewerContainer, data);
    })
    .catch(err => {
      console.error("Bracket fetch or parsing error:", err);
      alert("Failed to load bracket data.");
    });
}

/**
 * Sends a request to start the tournament (/start_tournament),
 * then refreshes the bracket view.
 */
function launchTournament() {
  fetch("/start_tournament", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert("Error: " + data.error);
        return;
      }
      alert("🚀 Tournament successfully launched!");
      generateBracket();
    })
    .catch(() => alert("Failed to start the tournament."));
}

/**
 * Sends a request to reset the tournament (/reset_tournament)
 * and clears the bracket viewer.
 */
function resetTournament() {
  fetch("/reset_tournament", { method: "POST" })
    .then(res => res.json())
    .then(() => {
      alert("⛔ Tournament has been reset.");
      document.getElementById("bracket-viewer").innerHTML = "";
    })
    .catch(() => alert("Failed to reset the tournament."));
}

/**
 * Updates the tournament status banner and toggles the launch button
 * depending on the number of players and current state.
 */
function updateTournamentStatus() {
  fetch("/tournament_status")
    .then(res => res.json())
    .then(data => {
      const label = document.getElementById("tournament-status-label");
      const count = document.getElementById("tournament-player-count");
      const container = document.getElementById("tournament-status");
      const launchBtn = document.getElementById("btn-launch-tournament");

      container.className = "alert d-flex justify-content-between align-items-center small";

      if (data.started) {
        container.classList.add("alert-success");
        label.innerHTML = `✅ Tournament running (since <strong>${new Date(data.started_at).toLocaleString()}</strong>)`;
      } else if (data.player_count >= 2) {
        container.classList.add("alert-warning");
        label.innerText = "⚠️ Ready to launch: enough players connected.";
      } else {
        container.classList.add("alert-danger");
        label.innerText = "⛔ Waiting: not enough players.";
      }

      count.innerText = `👥 ${data.player_count} player(s) connected`;

      if (data.player_count < 2 || data.started) {
        launchBtn.disabled = true;
        launchBtn.classList.add("disabled");
      } else {
        launchBtn.disabled = false;
        launchBtn.classList.remove("disabled");
      }
    });
}

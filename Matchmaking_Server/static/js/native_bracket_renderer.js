// native_bracket_renderer.js

/**
 * Renders a native single-elimination bracket into a container
 * @param {HTMLElement} container - The DOM element to render into
 * @param {Object} data - The bracket data object with stages and matches
 */
function renderNativeBracket(container, data) {
    container.innerHTML = "";
    container.classList.add("bracket-container");
  
    if (!data.matches || !Array.isArray(data.matches)) {
      container.innerHTML = "<div class='text-danger'>❌ Invalid bracket data structure.</div>";
      return;
    }
  
    const rounds = {};
  
    // Organize matches by round
    data.matches.forEach(match => {
      const round = match.round || 1;
      if (!rounds[round]) rounds[round] = [];
      rounds[round].push(match);
    });
  
    const roundNumbers = Object.keys(rounds).map(n => parseInt(n)).sort((a, b) => a - b);
    const roundNames = ["Round 1", "Quarter-finals", "Semi-finals", "Final", "Grand Final"];
  
    // Update current round indicator
    const currentRoundElement = document.getElementById("current-round");
    if (currentRoundElement && roundNumbers.length > 0) {
      currentRoundElement.textContent = roundNumbers.length;
    }
  
    // Update progress bar
    const progress = document.getElementById("round-progress");
    if (progress) {
      const percent = (roundNumbers.length / roundNames.length) * 100;
      progress.style.width = `${percent}%`;
      progress.textContent = `${Math.round(percent)}%`;
    }
  
    // Render rounds
    roundNumbers.forEach((roundNum, index) => {
      const matches = rounds[roundNum];
  
      const roundDiv = document.createElement("div");
      roundDiv.classList.add("bracket-round");
      roundDiv.dataset.round = roundNum;
  
      const roundLabel = document.createElement("div");
      roundLabel.classList.add("bracket-round-title");
      roundLabel.textContent = roundNames[index] || `Round ${roundNum}`;
      roundDiv.appendChild(roundLabel);
  
      matches.forEach((match, i) => {
        const matchDiv = document.createElement("div");
        matchDiv.classList.add("bracket-match");
        matchDiv.dataset.matchId = match.id;
  
        const p1 = match.opponent1?.name || (match.opponent1?.id ? "TBD" : "BYE");
        const p2 = match.opponent2?.name || (match.opponent2?.id ? "TBD" : "BYE");
        const winner = match.opponent1?.result === "win" ? p1 : match.opponent2?.result === "win" ? p2 : null;
  
        if (winner) {
          matchDiv.classList.add("winner");
        }
  
        matchDiv.innerHTML = `
          <div class="player">${p1}</div>
          <div class="vs">vs</div>
          <div class="player">${p2}</div>
          <div class="result">${winner ? "🏆 " + winner : ""}</div>
        `;
  
        matchDiv.addEventListener("click", () => {
          alert(`Match ID: ${match.id}\n${p1} vs ${p2}\n${winner ? "Winner: " + winner : "Winner: TBD"}`);
        });
  
        roundDiv.appendChild(matchDiv);
      });
  
      container.appendChild(roundDiv);
    });
  
    // Add legend
    const legend = document.createElement("div");
    legend.classList.add("bracket-legend", "mt-3", "small", "text-muted");
    legend.innerHTML = `
      <hr>
      <div><strong>Legend:</strong> <span class="mx-2">TBD = To Be Determined</span> | <span class="mx-2">BYE = No opponent</span> | <span class="mx-2">🏆 = Winner</span></div>
    `;
    container.appendChild(legend);
  }
  
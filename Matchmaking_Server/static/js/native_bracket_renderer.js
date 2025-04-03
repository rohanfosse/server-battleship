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
      container.innerHTML = "<div class='text-danger'>Invalid bracket data.</div>";
      return;
    }
  
    const rounds = {};
  
    data.matches.forEach(match => {
      const round = match.round || 1;
      if (!rounds[round]) rounds[round] = [];
      rounds[round].push(match);
    });
  
    Object.entries(rounds).sort((a, b) => a[0] - b[0]).forEach(([roundNum, matches]) => {
      const roundDiv = document.createElement("div");
      roundDiv.classList.add("bracket-round");
      roundDiv.dataset.round = roundNum;
  
      matches.forEach(match => {
        const matchDiv = document.createElement("div");
        matchDiv.classList.add("bracket-match");
  
        const p1 = match.opponent1?.name || "TBD";
        const p2 = match.opponent2?.name || "TBD";
        const winner = match.opponent1?.result === "win" ? p1 : match.opponent2?.result === "win" ? p2 : null;
  
        if (winner) {
          matchDiv.classList.add("winner");
        }
  
        matchDiv.innerHTML = `
          <div>${p1}</div>
          <div class="vs">vs</div>
          <div>${p2}</div>
          <div class="result">${winner ? "🏆 " + winner : ""}</div>
        `;
  
        roundDiv.appendChild(matchDiv);
      });
  
      container.appendChild(roundDiv);
    });
  }
  
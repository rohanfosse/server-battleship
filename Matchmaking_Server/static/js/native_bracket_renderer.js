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
    const totalRounds = roundNumbers.length;
  
    // Generate round names dynamically
    const roundNames = roundNumbers.map((roundNum, index) => {
      const remaining = totalRounds - index;
      if (remaining === 1) return "Final";
      if (remaining === 2) return "Semi-finals";
      if (remaining === 3) return "Quarter-finals";
      return `Round ${index + 1}`;
    });
  
    // Update current round indicator and progress
    const currentRoundElement = document.getElementById("current-round");
    if (currentRoundElement) currentRoundElement.textContent = roundNumbers.length;
  
    const progress = document.getElementById("round-progress");
    if (progress) {
      const percent = (roundNumbers.length / totalRounds) * 100;
      progress.style.width = `${percent}%`;
      progress.textContent = `${Math.round(percent)}%`;
    }
  
    // Clear any other modals before rendering
    document.querySelectorAll(".modal").forEach(m => m.remove());
  
    // Render each round
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
          if (p1 !== "TBD" && p2 !== "TBD" && p1 !== "BYE" && p2 !== "BYE") {
            const matchAlreadyStarted = match.opponent1?.result || match.opponent2?.result;
  
            // Avoid double modals
            document.querySelectorAll(".modal").forEach(m => m.remove());
  
            if (!matchAlreadyStarted) {
              launchMatchModal(p1, p2, match.id, matchDiv);
            } else {
              showWinnerModal(p1, p2, matchDiv);
            }
          }
        });
  
        roundDiv.appendChild(matchDiv);
      });
  
      container.appendChild(roundDiv);
    });
  }
  
  function launchMatchModal(p1, p2, matchId, matchDiv) {
    const modal = document.createElement("div");
    modal.classList.add("modal", "fade");
    modal.setAttribute("tabindex", "-1");
    modal.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Match Options</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Launch this match between <strong>${p1}</strong> and <strong>${p2}</strong>?</p>
          </div>
          <div class="modal-footer justify-content-between">
            <button class="btn btn-primary" id="launchBtn">Lancer le match</button>
          </div>
        </div>
      </div>
    `;
  
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
  
    modal.querySelector("#launchBtn").addEventListener("click", () => {
      fetch("/start_tournament_match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player1: p1, player2: p2, match_id: matchId })
      })
        .then(res => res.json())
        .then(response => {
          if (response.status === "match_started") {
            bsModal.hide();
            modal.remove();
            showWinnerModal(p1, p2, matchDiv);
          } else {
            alert("Error: " + (response.error || "Unknown error"));
          }
        })
        .catch(err => {
          console.error("Error launching match:", err);
          alert("An error occurred while launching the match.");
        });
    });
  }
  
  function showWinnerModal(p1, p2, matchDiv) {
    const modal = document.createElement("div");
    modal.classList.add("modal", "fade");
    modal.setAttribute("tabindex", "-1");
    modal.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Set Match Winner</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Who won the match between <strong>${p1}</strong> and <strong>${p2}</strong>?</p>
          </div>
          <div class="modal-footer justify-content-between">
            <button class="btn btn-outline-success" id="setWinner1">${p1}</button>
            <button class="btn btn-outline-danger" id="setWinner2">${p2}</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
  
    modal.querySelector("#setWinner1").addEventListener("click", () => submitResult(p1, p2, matchDiv, modal, bsModal));
    modal.querySelector("#setWinner2").addEventListener("click", () => submitResult(p2, p1, matchDiv, modal, bsModal));
  }
  
  function submitResult(winner, loser, matchDiv, modal, bsModal) {
    fetch("/match_result", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ winner, loser })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "result recorded") {
          matchDiv.querySelector(".result").innerHTML = `🏆 ${winner}`;
          matchDiv.classList.add("winner");
          matchDiv.classList.add("animate__animated", "animate__fadeInUp");
          setTimeout(() => {
            matchDiv.classList.remove("animate__animated", "animate__fadeInUp");
          }, 1000);
        } else {
          alert("Failed to record result: " + (data.error || "Unknown error"));
        }
      })
      .catch(err => {
        console.error("Error submitting result:", err);
        alert("An error occurred while submitting the result.");
      })
      .finally(() => {
        bsModal.hide();
        modal.remove();
      });
  }
  
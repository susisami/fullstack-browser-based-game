document.addEventListener('DOMContentLoaded', function() {

    if (!document.querySelector('.fa')) {
        console.warn("FontAwesome not loaded, using fallback");
        const faFallback = document.createElement('link');
        faFallback.rel = 'stylesheet';
        faFallback.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(faFallback);
    }

    async function fetchLeaderboard() {
        try {
            const response = await fetch('http://localhost:5000/game/users/leaderboards');
            const data = await response.json();

            if (response.status !== 200 || !data.Leaderboard) {
                throw new Error(data.Error || "Invalid server response");
            }

            renderLeaderboard(data.Leaderboard);
        } catch (error) {
            console.error("Leaderboard error:", error);
            document.getElementById('players-container').innerHTML = `
                <div class="error">
                    ${error.message}<br>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }
//laittaa pelaajaat sivustoon
    function renderLeaderboard(players) {
        const podium = document.getElementById('podium-container');
        const list = document.getElementById('players-container');

        if (!podium || !list) {
            console.error("Missing HTML containers!");
            return;
        }


        podium.innerHTML = players.slice(0, 3).map((player, i) => `
            <div class="podium-player ${['gold','silver','bronze'][i]}">
                <div class="rank">${i+1}</div>
                <i class="fas fa-user"></i>
                <div class="name">${player.username}</div>
                <div class="balance">${player.balance.toLocaleString()}T</div>
            </div>
        `).join('');

        list.innerHTML = players.slice(3).map(player => `
            <div class="player-row">
                <div class="rank">${player.rank}</div>
                <i class="fas fa-user"></i>
                <div class="name">${player.username}</div>
                <div class="balance">${player.balance.toLocaleString()}T</div>
            </div>
        `).join('');
    }

    fetchLeaderboard();
});
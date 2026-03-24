    // Load Game -lomake
    document.addEventListener("DOMContentLoaded", () => {
    loadGameForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = {
            Username: e.target.username.value,
            Password: e.target.password.value
        };

        if (!formData.Username || !formData.Password) {
        loadStatus.textContent = "Please enter both username and password.";
        return;
        }

        loadStatus.textContent = "Loading...";

        try {
            const response = await fetch("http://127.0.0.1:5000/game/users/load", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }

            const data = await response.json();
            console.log('Load game response:', data);

            if (data[0]['Loaded Personal Data']) {
                currentGameData = {
                    ...data[0]['Loaded Personal Data'],
                    'Real Time Data': data[0]['Real Time Data'] || {},
                    'Question': '',
                    quizStats: data[0]['Loaded Personal Data'].quizStats || {
                        totalCorrect: 0,
                        totalWrong: 0,
                        answeredAirports: {},
                        isFirstLocation: true
                    }
                };
                originalMapData = data[0]['Original Map Data'] || data[0]['Map Data'] || [];

                startGameArea(currentGameData, data[0]['Map Data'] || []);
                loadGameDialog.close();
            } else {
                loadStatus.textContent = "Invalid username or password.";
            }
        } catch (error) {
            console.error("Load Game Error:", error);
            loadStatus.textContent = error.message || "Failed to load game. Please try again.";
        }
    });
});

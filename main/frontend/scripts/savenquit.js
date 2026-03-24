// Save & Quit -toiminto
document.addEventListener("DOMContentLoaded", () => {
    saveAndQuitBtn.addEventListener("click", async () => {
        const statusElement = document.getElementById('saveStatus') || {
            textContent: '',
            style: { color: '' }
        };

        if (!currentGameData || !currentGameData.Username) {
            statusElement.textContent = "No game data to save. Start or load a game first.";
            statusElement.style.color = 'red';
            return;
        }

        try {
            statusElement.textContent = "Saving game...";
            statusElement.style.color = 'black';

            const saveData = {
                ...currentGameData,
                originalMapData: originalMapData
            };

            const response = await fetch("http://127.0.0.1:5000/game/users/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(saveData)
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();

            if (data.success !== false) {
                statusElement.textContent = data.message || "Game saved successfully!";
                statusElement.style.color = 'green';
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                throw new Error(data.message || "Save operation failed");
            }
        } catch (error) {
            console.error("Save Game Error:", error);
            statusElement.textContent = error.message || "Failed to save game. Please try again.";
            statusElement.style.color = 'red';
            setTimeout(() => {
                statusElement.textContent = "";
            }, 3000);
        }
    });
});

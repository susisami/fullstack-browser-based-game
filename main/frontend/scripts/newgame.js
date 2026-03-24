// New Game Form
document.addEventListener("DOMContentLoaded", () => {
newGameForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        Username: e.target.username.value.trim(),
        Password: e.target.password.value.trim(),
    };
    //status element
    const statusElement = document.getElementById('newGameStatus');

    // Validate inputs
    if (!formData.Username || !formData.Password) {
        if (statusElement) statusElement.textContent = "Please enter both username and password.";
        return;
    }

    if (statusElement) statusElement.textContent = "Creating new game...";

    try {
        // Send data to backend
        const response = await fetch('http://127.0.0.1:5000/game/users/insert', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData),
        });

        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
        const data = await response.json();

        // Check if data is valid and contains expected structure
        if (!data || !data[0] || !data[0]['Airport Data']) {
            throw new Error('Invalid response data structure from server');
        }

        console.log('Backend response:', data);
        currentGameData = {
            Username: formData.Username,
            Balance: data[0]['Airport Data']['Balance'],
            Airport: data[0]['Airport Data']['Airport'],
            Country: data[0]['Airport Data']['Country'],
            ICAO: data[0]['Airport Data']['ICAO'],
            Continent: data[0]['Airport Data']['Continent'],
            Latitude: data[0]['Airport Data']['Latitude & Longitude'][0],
            Longitude: data[0]['Airport Data']['Latitude & Longitude'][1],
            'Visited Countries': 0,
            'Traveled kilometers': 0,
            'Real Time Data': data[0]['Real Time Data'] || {},
            'Question': data[0]['Question'] || '',
            quizStats: {
                totalCorrect: 0,
                totalWrong: 0,
                answeredAirports: {}
            }
        };

        originalMapData = data[0]['Map Data'] || [];
        startGameArea(currentGameData, originalMapData);
        newGameDialog.close();

    } catch (error) {
        console.error('New Game Error:', error);
        if (statusElement) {
            statusElement.textContent = error.message || "Failed to create game. Please try again.";
        } else {
            // error if status element is missing
            alert(error.message || "Failed to create game. Please try again.");
        }
    }
 });
});

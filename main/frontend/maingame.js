// Elementtien valinta
const mainMenu = document.getElementById("mainMenu");
const newGameBtn = document.getElementById("newGame");
const loadGameBtn = document.getElementById("loadGame");
const saveAndQuitBtn = document.getElementById("saveAndQuit");
const quitGameBtn = document.getElementById("quitGame");
const newGameDialog = document.getElementById("newGameDialog");
const loadGameDialog = document.getElementById("loadGameDialog");
const newGameForm = document.getElementById("newGameForm");
const loadGameForm = document.getElementById("loadGameForm");
const loadStatus = document.getElementById("loadStatus");
const cancelNewGame = document.getElementById("cancelNewGame");
const cancelLoadGame = document.getElementById("cancelLoadGame");
const gameArea = document.getElementById("gameArea");
const newGameStatus = document.getElementById("newGameStatus");
const saveStatus = document.getElementById("saveStatus");
let currentGameData = {
    Question: '' //Start with empty question
};
let quizStats = {totalCorrect: 0, totalWrong: 0, answeredAirports: {}};
let planeMarker = null;
let originalMapData = null;
let isFlying = false;
let map;
let correctAnswerMarkers = [];
let incorrectAnswerMarkers = [];
let isQuizInProgress = false;

document.addEventListener("DOMContentLoaded",() =>{
    mainMenu.showModal();

    // Päävalikon toiminnot
    newGameBtn.addEventListener("click", () => {
        mainMenu.close();
        newGameDialog.showModal();
        const statusElement = document.getElementById('newGameStatus');
        if (statusElement) statusElement.textContent = "";
    });

    loadGameBtn.addEventListener("click", () => {
        mainMenu.close();
        loadGameDialog.showModal();
        loadStatus.textContent = "";
    });

    quitGameBtn.addEventListener("click", () => {
        if (confirm("Haluatko varmasti sulkea pelin?")) {
            window.location.reload();
        }
    });

    // Peruuta-napit
    cancelNewGame.addEventListener("click", () => {
        newGameDialog.close();
        mainMenu.showModal();
    });
    cancelLoadGame.addEventListener("click", () => {
        loadGameDialog.close();
        mainMenu.showModal();
    });
});

async function startGameArea(playerData, mapData) {
    uiUXUpdate(playerData);

    // Stores original map data if not already stored
    if (!originalMapData && mapData) {
        originalMapData = mapData;
    }

    // Merges new data with existing currentGameData to preserve all properties
    currentGameData = {
        ...currentGameData,
        ...playerData,
        // Ensure quizStats is properly maintained
        quizStats: currentGameData.quizStats || {
            totalCorrect: 0,
            totalWrong: 0,
            answeredAirports: {},
            isFirstLocation: true
        }
    };

    console.log("Current game data:", currentGameData);

    const currentLocationKey = `${currentGameData.Latitude},${currentGameData.Longitude}`;

    if (map) {
        // Only remove the plane marker and recreate current position
        if (planeMarker) map.removeLayer(planeMarker);
        map.eachLayer(layer => {
            if (layer instanceof L.Marker &&
                !correctAnswerMarkers.includes(layer) &&
                !incorrectAnswerMarkers.includes(layer)) {
                map.removeLayer(layer);
            }
        });
    } else {
        // Initialize new map if it doesnt exist
        map = L.map('map').setView([currentGameData.Latitude, currentGameData.Longitude], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
            maxZoom: 19
        }).addTo(map);
    }

    // Create current airport marker with green icon
    const currentMarker = L.marker([currentGameData.Latitude, currentGameData.Longitude], {
        icon: L.divIcon({
            className: 'current-airport-icon',
            html: '<i class="fas fa-plane" style="color: #2ecc71; font-size: 24px;"></i>',
            iconSize: [30, 30]
        })
    }).addTo(map);

    // Full airport information display
    let popupContent = `
        <b>Current Airport</b><br>${currentGameData.Airport}</b>
        <br>
        <b class="airport-info">ICAO-code: [${currentGameData.ICAO}]</b>
        <br>               
        <b class="airport-info">Country: [${currentGameData.Country}]</b>
        <br>
        <b class="airport-info">Continent: [${currentGameData.Continent}]</b>
        <br>
        <b class="airport-info">Latitude: [${currentGameData.Latitude}]</b>
        <br>
        <b class="airport-info">Longitude: [${currentGameData.Longitude}]</b>
        <br>
        <b class="airport-info">Quiz Stats: ${currentGameData.quizStats.totalCorrect} correct, ${currentGameData.quizStats.totalWrong} wrong</b>
        <br>`;

    // Add realtime data if available
    if (currentGameData['Real Time Data']) {
        popupContent += `
        <article class="real-time-info"> 
            <div> ${currentGameData['Real Time Data']['Temperature_Celsius']}° </div>
            <div> ${currentGameData['Real Time Data']['Temperature_Condition']} </div>
            <div> ${currentGameData['Real Time Data']['Temperature_Kelvin']}K</div>
        </article>`;
    }

    currentMarker.bindPopup(popupContent).openPopup();

    // Create destination markers from original data
    for (const airport of originalMapData) {
        const lat = Number(airport.lat);
        const lng = Number(airport.lon);

        if (isNaN(lat) || isNaN(lng)) {
            console.error('Invalid coordinates for airport:', airport.name);
            continue;
        }

        // Check if this airport has been answered before or is current location
        const airportKey = `${lat},${lng}`;
        const isAnswered = currentGameData.quizStats.answeredAirports[airportKey];
        const isCurrentLocation = lat === currentGameData.Latitude && lng === currentGameData.Longitude;

        // Skip creating marker if:
        // 1. Already answered or
        // 2. Is current location
        if (isAnswered || (isCurrentLocation && !currentGameData.quizStats.isFirstLocation)) continue;

        const marker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'destination-marker',
                html: '<i class="fas fa-map-marker-alt" style="color: #3498db;"></i>',
                iconSize: [25, 25]
            })
        }).addTo(map);

        marker.bindPopup(`
            <b class="airport-info-name">${airport.name}</b>
            <br>
            <b class="airport-info">ICAO-code: [${airport.icao}]</b>
            <br>               
            <b class="airport-info">Municipality: ${airport.city}</b>
            <br>
            <b class="airport-info">Country: ${airport.country}</b>
            <br>
            <b class="airport-info">Continent: [${airport.continent}]</b>
            <br>
            <b class="airport-info">Latitude: ${airport.lat}</b>
            <br>
            <b class="airport-info">Longitude: ${airport.lon}</b>
            <br>
            <button class="travel">Travel</button>`);

        marker.on('popupopen', () => {
            const travelButtons = document.querySelectorAll('button.travel');
            for (let i = 0; i < travelButtons.length; i++) {
                travelButtons[i].addEventListener('click', async () => {
                    if (isFlying) return;
                    isFlying = true;

                    try {
                        // Store the destination coordinates before removing anything
                        const destCoords = [airport.lat, airport.lon];

                        travelButtons[i].textContent = "Preparing...";
                        travelButtons[i].disabled = true;

                        await new Promise(resolve => setTimeout(resolve, 500));

                        travelButtons[i].textContent = "Flying...";

                        const updateData = {
                            'New Game Data' : {
                                'Username' : currentGameData.Username,
                                'New Airport' : airport.name,
                                'New Municipality' : airport.city,
                                'New Country' : airport.country,
                                'New Continent' : airport.continent,
                                'New Latitude' : airport.lat,
                                'New Longitude' : airport.lon,
                                'New ICAO' : airport.icao
                            },
                            'Old Game Data' : {
                                ...currentGameData,
                                quizStats: {
                                    ...currentGameData.quizStats,
                                    isFirstLocation: false
                                }
                            }
                        };

                        const response = await fetch('http://127.0.0.1:5000/game/users/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(updateData)
                        });

                        if (!response.ok) throw new Error(`HTTP Error, Status ${response.status}`);

                        const data = await response.json();

                        // Save old position before updating
                        const oldCoords = [currentGameData.Latitude, currentGameData.Longitude];
                                
                        // Remove the current plane marker before animation starts
                        map.removeLayer(currentMarker); // Removes the green marker

                        // Animate flight use oldCoords > destCoords
                        await animateFlight(oldCoords, destCoords);

                        // Now merge the new data with existing currentGameData
                        currentGameData = {
                            ...currentGameData,
                            ...data[0]['Personal & Airport Data'],
                            'Real Time Data': data[0]['Real Time Data'],
                            'Question': data[0]['Question'],
                            'Traveled kilometers': data[0]['Personal & Airport Data']['Traveled Kilometers'] ||
                                                data[0]['Personal & Airport Data']['Traveled kilometers'] || 0,
                            quizStats: {
                                ...currentGameData.quizStats,
                                isFirstLocation: false
                            }
                        };

                        // Animate flight - don't remove markers yet
                        await animateFlight(
                            [currentGameData.Latitude, currentGameData.Longitude],
                            destCoords
                        );

                        travelButtons[i].textContent = "Landing...";
                        await new Promise(resolve => setTimeout(resolve, 500));

                        // Now remove the markers and update the game area
                        if (currentMarker) map.removeLayer(currentMarker);
                        if (marker) map.removeLayer(marker);

                        // Update the game area
                        startGameArea(currentGameData, originalMapData);

                        // Automatically start quiz if conditions are met
                        const currentLocationKey = `${currentGameData.Latitude},${currentGameData.Longitude}`;
                        if (!currentGameData.quizStats.isFirstLocation &&
                            currentGameData['Question'] &&
                            currentGameData['Question'].question &&
                            !currentGameData.quizStats.answeredAirports[currentLocationKey]) {
                            setTimeout(() => {
                                isQuizInProgress = true;
                                questionModal(currentGameData['Question']);
                            }, 1000); // Small delay after landing
                        }

                    } catch (error) {
                        console.error('Travel failed:', error);
                        if (travelButtons[i]) {
                            travelButtons[i].textContent = "Travel";
                            travelButtons[i].disabled = false;
                        }
                        alert("Travel failed. Please try again.");
                    } finally {
                        isFlying = false;
                    }
                });
            }
        });
    }

    // Restore answer markers from saved data
    for (const [coords, result] of Object.entries(currentGameData.quizStats.answeredAirports)) {
        const [lat, lng] = coords.split(',').map(Number);
        if (result === 'correct') {
            const marker = L.marker([lat, lng], {
                icon: L.divIcon({
                    className: 'correct-marker',
                    html: '<i class="fas fa-check" style="color: #2ecc71;"></i>',
                    iconSize: [25, 25]
                })
            }).addTo(map);
            correctAnswerMarkers.push(marker);
        } else if (result === 'wrong') {
            const marker = L.marker([lat, lng], {
                icon: L.divIcon({
                    className: 'incorrect-marker',
                    html: '<i class="fas fa-times" style="color: #e74c3c;"></i>',
                    iconSize: [25, 25]
                })
            }).addTo(map);
            incorrectAnswerMarkers.push(marker);
            }
        }
    }

async function animateFlight(startCoords, endCoords) {
    return new Promise((resolve) => {
        if (planeMarker) map.removeLayer(planeMarker);

        // Convert to maps pixel coordinates
        const zoom = map.getZoom();
        const startPoint = map.project(startCoords, zoom);
        const endPoint = map.project(endCoords, zoom);

        const bearing = Math.atan2(endCoords[1] - startCoords[1], endCoords[0] - startCoords[0]) * 180 / Math.PI;
        const adjustedBearing = bearing + 270;

        planeMarker = L.marker(startCoords, {
            icon: L.divIcon({
                className: 'plane-icon',
                html: `<i class="fas fa-plane" style="transform: rotate(${adjustedBearing}deg);"></i>`,
                iconSize: [30, 30]
            })
        }).addTo(map);

        const duration = 2000; // ms
        const startTime = Date.now();

        function animate() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Interpolate in pixels
            const currentPoint = L.point(
                startPoint.x + (endPoint.x - startPoint.x) * progress,
                startPoint.y + (endPoint.y - startPoint.y) * progress
            );

            const currentLatLng = map.unproject(currentPoint, zoom);
            planeMarker.setLatLng(currentLatLng);

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                map.removeLayer(planeMarker);
                resolve();
            }
        }

        requestAnimationFrame(animate);
    });
}

function mapLayers() {
    const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    });

    const osmHOT = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team hosted by OpenStreetMap France'
    });

    const openTopoMap = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'
    });

    return {
        'Street Map' : osm,
        'Street Map HOT' : osmHOT,
        'Topography Map' : openTopoMap
    };
}

function questionModal(questionData) {
    console.log('Creating question modal with:', questionData);

    const modal = document.createElement('dialog');
    modal.classList.add('quiz-dialog');

    const h2 = document.createElement('h2');
    h2.innerText = `${questionData['question']}`;

    const answer = document.createElement('input');
    answer.type = 'text';
    answer.placeholder = 'Enter an answer';
    answer.id = 'quiz';
    answer.classList.add('quiz-answer');

    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.textContent = 'Submit';
    submitButton.classList.add('quiz-submit');

    const form = document.createElement('form');
    form.id = 'quiz-form';
    form.classList.add('quiz-form');
    form.appendChild(answer);
    form.appendChild(submitButton);

    const paragraph = document.createElement('p');
    paragraph.id = 'answer';
    paragraph.classList.add('quiz-balance-addition');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const result = answer.value;
        console.log('Question answered:', result);
        answer.disabled = true;
        submitButton.disabled = true;

        const airportKey = `${currentGameData.Latitude},${currentGameData.Longitude}`;

        // Update stats immediately
        if (result == questionData['answer']) {
            console.log('Correct answer!');
            currentGameData.Balance += 1250;
            currentGameData.quizStats.totalCorrect++;
            currentGameData.quizStats.answeredAirports[airportKey] = 'correct';

            paragraph.style.color = 'green';
            paragraph.textContent = `Balance increased by 1250T's`;
            const correctMarker = L.marker([currentGameData.Latitude, currentGameData.Longitude], {
                icon: L.divIcon({
                    className: 'correct-marker',
                    html: '<i class="fas fa-check" style="color: #2ecc71;"></i>',
                    iconSize: [25, 25]
                })
            }).addTo(map);
            correctAnswerMarkers.push(correctMarker);
        } else {
            console.log('Wrong answer!');
            currentGameData.Balance -= 1000;
            currentGameData.quizStats.totalWrong++;
            currentGameData.quizStats.answeredAirports[airportKey] = 'wrong';

            paragraph.style.color = 'red';
            paragraph.textContent = `Balance decreased by 1000T's`;

            const incorrectMarker = L.marker([currentGameData.Latitude, currentGameData.Longitude], {
                icon: L.divIcon({
                    className: 'incorrect-marker',
                    html: '<i class="fas fa-times" style="color: #e74c3c;"></i>',
                    iconSize: [25, 25]
                })
            }).addTo(map);
            incorrectAnswerMarkers.push(incorrectMarker);
        }

        //ppdate ui instantly (no waiting for travel)
        uiUXUpdate(currentGameData);

        //check for victory right after balance update
        if (currentGameData.Balance >= 50000) {
        endGame(currentGameData, true);
        return;
        }

        // Save the updated game state in background
        setTimeout(async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/game/users/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        'Old Game Data': currentGameData,
                        'New Game Data': currentGameData
                    })
                });

                if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

                const data = await response.json();
                console.log('Game state saved:', data);
            } catch (error) {
                console.error('Failed to save game state:', error);
            }
        }, 0);

        setTimeout(() => {
            modal.close();
            modal.remove();
            isQuizInProgress = false;

            // Refresh all popups
            map.eachLayer(layer => {
                if (layer instanceof L.Marker) {
                    const latLng = layer.getLatLng();
                    if (latLng.lat === currentGameData.Latitude &&
                        latLng.lng === currentGameData.Longitude) {
                        layer.closePopup();
                        layer.openPopup();
                    }
                }
            });
        }, 1000);
    });

    const oldModal = document.querySelector('dialog.quiz-dialog');
    if (oldModal) {
        oldModal.remove();
    }

    modal.appendChild(h2);
    modal.appendChild(form);
    modal.appendChild(paragraph);
    document.querySelector('main').appendChild(modal);
    modal.showModal();
}

function toCloseQuizModal() {
    console.log('Closing quiz modal');
    const quizDialog = document.querySelector('dialog.quiz-dialog');
    if (quizDialog && quizDialog.open) {
        quizDialog.close();
        quizDialog.style.display = 'none';
        quizDialog.removeAttribute('open');
    }
}

function uiUXUpdate(updateData) {
    // Safely update elements if they exist
    const safeUpdate = (id, value) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    };

    // Update all UI elements
    safeUpdate('balanceValue', updateData['Balance']);
    safeUpdate('SecondBalanceValue', updateData['Balance']);
    safeUpdate('currentAirportValue', updateData['Airport']);
    safeUpdate('distanceValue', `${updateData['Visited Countries']} kpl`);
    safeUpdate('distancekmValue', `${updateData['Traveled kilometers']} km`);

    // Update dropdown username
    const dropdownLink = document.querySelector('nav[title="dropdown"] a');
    if (dropdownLink) {
        dropdownLink.innerHTML = `${updateData['Username']} <i class="fa-solid fa-caret-down"></i>`;
    }

    if (updateData.Balance >= 50000 || updateData.Balance <= 0) {
        console.log(`Game ends with balance of ${updateData.Balance}`);
        endGame(updateData, true);
        return
    }
}

function endGame(endData){
    let endText;

    if (endData['Balance'] >= 50000){
        endText = `Congratulations ${endData['Username']}, you won the game!`
    }

    else if (endData['Balance'] <= 0) {
        endText = `Sadly ${endData['Username']}, you lost the game!`
    }

    /*Ending dialog*/

    //End dialog
    const endDialog = document.createElement('dialog');
    endDialog.classList.add('ending-dialog');

    //End title
    const endTitle = document.createElement('h1');
    endTitle.classList.add('ending-title');
    endTitle.innerText = `${endText}`;

    //Ending stats list
    const endUl = document.createElement('ul');
    endUl.classList.add('ending-stats-list');

    //Ending stats list elements
    const li1 = document.createElement('li');
    li1.classList.add('ending-stats-list-element');
    li1.innerText = `Balance: ${endData['Balance']} T`;

    const li2 = document.createElement('li');
    li2.classList.add('ending-stats-list-element');
    li2.innerText = `Last Airport: ${endData['Airport']}`;

    const li3 = document.createElement('li');
    li3.classList.add('ending-stats-list-element');
    li3.innerText = `Last Airport: ${endData['Country']} [${endData['ICAO']}]`;

    const li4 = document.createElement('li');
    li4.classList.add('ending-stats-list-element');
    li4.innerText = `Last Continent: ${endData['Continent']}`;

    const li5 = document.createElement('li');
    li5.classList.add('ending-stats-list-element');
    li5.innerText = `Visited Airports: ${endData['Visited Countries']}`;

    const li6 = document.createElement('li');
    li6.classList.add('ending-stats-list-element');
    li6.innerText = `Total Travel Kilometers: ${endData['Traveled kilometers']}`;

    const endingParagraph = document.createElement('p');
    endingParagraph.classList.add('ending-paragraph');
    endingParagraph.innerText = `You've completed the game now and will not be able to play anymore. Please share your feedback/ideas for future development!`

    const endButton = document.createElement('button');
    endButton.classList.add('ending-button');
    endButton.innerHTML = `<i class="fa-solid fa-right-from-bracket"></i>`
    endButton.addEventListener('click', async () => {
        if (endData['Balance'] <= 0) {
            const response = await fetch('http://127.0.0.1:5000/game/users/delete', {
                method: 'POST',
                headers: {'Content-Type' : 'application/json'},
                body: JSON.stringify({'Username' : endData['Username']})
            });

            const data = response.json()
            endButton.textContent = `${data['Message']}`;

            setTimeout(() => {window.location.reload()}, 5000)
        }

        else {
            endButton.style.backgroundColor = 'rgb(125, 246, 131)';
            endButton.textContent = `User information saved!`
            setTimeout(() => {window.location.reload()}, 5000)
        }
    })

    endDialog.appendChild(endTitle);
    endUl.appendChild(li1);
    endUl.appendChild(li2);
    endUl.appendChild(li3);
    endUl.appendChild(li4);
    endUl.appendChild(li5);
    endUl.appendChild(li6);
    endDialog.appendChild(endUl);
    endDialog.appendChild(endingParagraph);
    endDialog.appendChild(endButton);
    document.querySelector('main').appendChild(endDialog);
    endDialog.showModal()
};

//m=ake functions available globally for inline event handlers
window.questionModal = questionModal;
window.toCloseQuizModal = toCloseQuizModal;

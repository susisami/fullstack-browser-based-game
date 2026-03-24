# Browser-Based Flight Game

## Overview

A full stack browser-based flight game where the player travels between airports, answers location-based questions, and earns in-game currency. The game integrates external REST APIs to provide real-time data and dynamic gameplay.

The objective is to reach **30,000 T** by traveling and correctly answering questions related to the player’s current location.

---

## Key Features

* Full stack architecture (Python backend + browser frontend)
* REST API integration for real-time data
* Location-based gameplay using real-world data
* User authentication with secure password hashing
* Dynamic UI updates using JavaScript and AJAX
* Persistent game state stored in a relational database

---

## External APIs

The game utilizes multiple external REST APIs:

* **OpenWeatherMap API**
  → Fetches real-time weather data based on player location

* **REST Countries API**
  → Generates location-based questions related to the current country

---

## Game Logic

1. Player starts at an airport
2. Player travels between locations (airports)
3. Game fetches real-time data (weather, country info)
4. Player answers questions based on the current location
5. Correct answers reward in-game currency
6. Game ends when the player reaches **30,000 T**

---

## Architecture

The system consists of:

* **Backend (Python / Flask)**

  * Handles game logic and API endpoints
  * Communicates with external APIs
  * Manages database operations

* **Frontend (HTML, CSS, JavaScript)**

  * Displays game interface
  * Sends requests via AJAX

* **Database (MySQL)**

  * Stores user data, game state, and progress

---

## Backend Structure

The backend follows an object-oriented design:

* A central **SqlConnection** class manages all database connections
* Other classes inherit from this base class
* Ensures structured and reusable database interaction

---

## Technologies

* Python (Flask)
* SQL (MySQL)
* JavaScript (AJAX)
* HTML & CSS
* REST APIs
* OpenWeatherMap API
* REST Countries API

---

## Setup & Run

### 1. Clone the repository

```bash
git clone https://github.com/susisami/your-repo.git
cd your-repo
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file or configure variables manually:

```bash
DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
OPENWEATHER_API_KEY=your_api_key
```

### 4. Run the application

```bash
python app.py
```

---

## Database

The game uses a relational database structure consisting of:

* Game (player data and progress)
* Airport (location data)
* Country (country-related data)
* Feedback (user feedback)

---

## Future Improvements

* Improved UI/UX design
* More diverse question system
* Expanded gameplay mechanics
* Better data visualization

---

## Author

Sami Souci



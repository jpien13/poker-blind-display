from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Default tournament structure if none exists
default_tournament = {
    "name": "Default Tournament",
    "levels": [
        {"level": 1, "small_blind": 5, "big_blind": 10, "ante": 0, "duration": 15},
        {"level": 2, "small_blind": 10, "big_blind": 20, "ante": 0, "duration": 15},
        {"level": 3, "small_blind": 15, "big_blind": 30, "ante": 0, "duration": 15},
        {"level": 4, "small_blind": 25, "big_blind": 50, "ante": 0, "duration": 15},
        {"level": 5, "small_blind": 50, "big_blind": 100, "ante": 5, "duration": 15},
        {"level": 6, "small_blind": 75, "big_blind": 150, "ante": 10, "duration": 15},
        {"level": 7, "small_blind": 100, "big_blind": 200, "ante": 25, "duration": 15},
        {"level": 8, "small_blind": 150, "big_blind": 300, "ante": 25, "duration": 15},
    ]
}

DATA_FILE = 'tournament_data.json'

def load_tournament_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return default_tournament

def save_tournament_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    tournament = load_tournament_data()
    return render_template('index.html', tournament=tournament)

@app.route('/timer')
def timer():
    tournament = load_tournament_data()
    return render_template('timer.html', tournament=tournament)

@app.route('/admin')
def admin():
    tournament = load_tournament_data()
    return render_template('admin.html', tournament=tournament)

@app.route('/api/tournament', methods=['GET'])
def get_tournament():
    return jsonify(load_tournament_data())

@app.route('/api/tournament', methods=['POST'])
def update_tournament():
    data = request.json
    save_tournament_data(data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Create templates and static folders if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Create HTML templates
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poker Tournament Timer</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Poker Tournament Timer</h1>
        <div class="buttons">
            <a href="/timer" class="btn">Start Timer</a>
            <a href="/admin" class="btn">Admin Setup</a>
        </div>
    </div>
</body>
</html>
''')
    
    with open('templates/timer.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poker Tournament Timer</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container timer-container">
        <h1 id="tournament-name">{{ tournament.name }}</h1>
        
        <div class="timer-display">
            <div class="time-remaining">
                <h2>Time Remaining</h2>
                <div id="timer" class="timer">15:00</div>
            </div>
            
            <div class="current-level">
                <h2>Current Level</h2>
                <div class="level-info">
                    <div class="level-number">Level <span id="current-level">1</span></div>
                    <div class="blinds">
                        <div class="blind">Small Blind: <span id="current-small-blind">5</span></div>
                        <div class="blind">Big Blind: <span id="current-big-blind">10</span></div>
                        <div class="blind">Ante: <span id="current-ante">0</span></div>
                    </div>
                </div>
            </div>
            
            <div class="next-level">
                <h2>Next Level</h2>
                <div class="level-info">
                    <div class="level-number">Level <span id="next-level">2</span></div>
                    <div class="blinds">
                        <div class="blind">Small Blind: <span id="next-small-blind">10</span></div>
                        <div class="blind">Big Blind: <span id="next-big-blind">20</span></div>
                        <div class="blind">Ante: <span id="next-ante">0</span></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="timer-controls">
            <button id="start-btn" class="btn control-btn">Start</button>
            <button id="pause-btn" class="btn control-btn" disabled>Pause</button>
            <button id="reset-btn" class="btn control-btn">Reset</button>
            <button id="next-level-btn" class="btn control-btn">Next Level</button>
            <button id="prev-level-btn" class="btn control-btn">Previous Level</button>
        </div>
        
        <div class="home-link">
            <a href="/" class="btn">Home</a>
        </div>
    </div>

    <script>
        // Tournament data
        const tournamentData = {{ tournament|tojson|safe }};
        let currentLevelIndex = 0;
        let timerInterval;
        let timeRemaining = tournamentData.levels[0].duration * 60; // in seconds
        let isPaused = true;
        
        // Elements
        const timerEl = document.getElementById('timer');
        const currentLevelEl = document.getElementById('current-level');
        const currentSmallBlindEl = document.getElementById('current-small-blind');
        const currentBigBlindEl = document.getElementById('current-big-blind');
        const currentAnteEl = document.getElementById('current-ante');
        const nextLevelEl = document.getElementById('next-level');
        const nextSmallBlindEl = document.getElementById('next-small-blind');
        const nextBigBlindEl = document.getElementById('next-big-blind');
        const nextAnteEl = document.getElementById('next-ante');
        const startBtn = document.getElementById('start-btn');
        const pauseBtn = document.getElementById('pause-btn');
        const resetBtn = document.getElementById('reset-btn');
        const nextLevelBtn = document.getElementById('next-level-btn');
        const prevLevelBtn = document.getElementById('prev-level-btn');
        
        // Update display
        function updateDisplay() {
            const currentLevel = tournamentData.levels[currentLevelIndex];
            const nextLevel = currentLevelIndex < tournamentData.levels.length - 1 
                ? tournamentData.levels[currentLevelIndex + 1] 
                : null;
            
            // Update current level
            currentLevelEl.textContent = currentLevel.level;
            currentSmallBlindEl.textContent = currentLevel.small_blind;
            currentBigBlindEl.textContent = currentLevel.big_blind;
            currentAnteEl.textContent = currentLevel.ante;
            
            // Update next level if available
            if (nextLevel) {
                nextLevelEl.textContent = nextLevel.level;
                nextSmallBlindEl.textContent = nextLevel.small_blind;
                nextBigBlindEl.textContent = nextLevel.big_blind;
                nextAnteEl.textContent = nextLevel.ante;
                document.querySelector('.next-level').style.display = 'block';
            } else {
                document.querySelector('.next-level').style.display = 'none';
            }
            
            // Update timer
            updateTimer();
        }
        
        // Update timer display
        function updateTimer() {
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timerEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Change color as time gets low
            if (timeRemaining <= 60) {
                timerEl.classList.add('warning');
            } else {
                timerEl.classList.remove('warning');
            }
        }
        
        // Start timer
        function startTimer() {
            isPaused = false;
            startBtn.disabled = true;
            pauseBtn.disabled = false;
            
            timerInterval = setInterval(() => {
                if (timeRemaining > 0) {
                    timeRemaining--;
                    updateTimer();
                } else {
                    // Auto advance to next level
                    if (currentLevelIndex < tournamentData.levels.length - 1) {
                        goToNextLevel();
                    } else {
                        clearInterval(timerInterval);
                        timerEl.textContent = "FINISHED";
                    }
                }
            }, 1000);
        }
        
        // Pause timer
        function pauseTimer() {
            isPaused = true;
            clearInterval(timerInterval);
            startBtn.disabled = false;
            pauseBtn.disabled = true;
        }
        
        // Reset current level
        function resetTimer() {
            pauseTimer();
            timeRemaining = tournamentData.levels[currentLevelIndex].duration * 60;
            updateTimer();
        }
        
        // Go to next level
        function goToNextLevel() {
            if (currentLevelIndex < tournamentData.levels.length - 1) {
                pauseTimer();
                currentLevelIndex++;
                timeRemaining = tournamentData.levels[currentLevelIndex].duration * 60;
                updateDisplay();
                
                // Play sound alert
                const audio = new Audio('/static/level-up.mp3');
                audio.play().catch(e => console.log('Audio failed to play: ', e));
                
                // Start timer automatically
                startTimer();
            }
        }
        
        // Go to previous level
        function goToPrevLevel() {
            if (currentLevelIndex > 0) {
                pauseTimer();
                currentLevelIndex--;
                timeRemaining = tournamentData.levels[currentLevelIndex].duration * 60;
                updateDisplay();
            }
        }
        
        // Event listeners
        startBtn.addEventListener('click', startTimer);
        pauseBtn.addEventListener('click', pauseTimer);
        resetBtn.addEventListener('click', resetTimer);
        nextLevelBtn.addEventListener('click', goToNextLevel);
        prevLevelBtn.addEventListener('click', goToPrevLevel);
        
        // Initialize
        updateDisplay();
    </script>
</body>
</html>
''')
    
    with open('templates/admin.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tournament Setup</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container admin-container">
        <h1>Tournament Setup</h1>
        
        <form id="tournament-form">
            <div class="form-group">
                <label for="tournament-name">Tournament Name:</label>
                <input type="text" id="tournament-name" required>
            </div>
            
            <h2>Blind Structure</h2>
            <div id="levels-container">
                <!-- Levels will be added here dynamically -->
            </div>
            
            <button type="button" id="add-level-btn" class="btn">Add Level</button>
            
            <div class="form-actions">
                <button type="submit" class="btn">Save Tournament</button>
                <a href="/" class="btn">Cancel</a>
            </div>
        </form>
    </div>

    <script>
        // Tournament data
        let tournamentData = {{ tournament|tojson|safe }};
        
        // Elements
        const tournamentNameInput = document.getElementById('tournament-name');
        const levelsContainer = document.getElementById('levels-container');
        const addLevelBtn = document.getElementById('add-level-btn');
        const form = document.getElementById('tournament-form');
        
        // Load existing data
        function loadTournamentData() {
            tournamentNameInput.value = tournamentData.name;
            
            // Clear existing levels
            levelsContainer.innerHTML = '';
            
            // Add each level
            tournamentData.levels.forEach((level, index) => {
                addLevelRow(level, index);
            });
        }
        
        // Add a new level row
        function addLevelRow(level = {}, index) {
            const levelNumber = level.level || (tournamentData.levels.length + 1);
            const smallBlind = level.small_blind || 0;
            const bigBlind = level.big_blind || 0;
            const ante = level.ante || 0;
            const duration = level.duration || 15;
            
            const levelRow = document.createElement('div');
            levelRow.className = 'level-row';
            levelRow.innerHTML = `
                <div class="level-number">Level ${levelNumber}</div>
                <div class="level-inputs">
                    <div class="form-group">
                        <label for="small-blind-${index}">Small Blind:</label>
                        <input type="number" id="small-blind-${index}" value="${smallBlind}" min="1" required>
                    </div>
                    <div class="form-group">
                        <label for="big-blind-${index}">Big Blind:</label>
                        <input type="number" id="big-blind-${index}" value="${bigBlind}" min="2" required>
                    </div>
                    <div class="form-group">
                        <label for="ante-${index}">Ante:</label>
                        <input type="number" id="ante-${index}" value="${ante}" min="0" required>
                    </div>
                    <div class="form-group">
                        <label for="duration-${index}">Duration (min):</label>
                        <input type="number" id="duration-${index}" value="${duration}" min="1" required>
                    </div>
                    <button type="button" class="btn remove-btn" data-index="${index}">Remove</button>
                </div>
            `;
            
            levelsContainer.appendChild(levelRow);
        }
        
        // Add event listeners for remove buttons
        function addRemoveListeners() {
            document.querySelectorAll('.remove-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    const index = parseInt(e.target.dataset.index);
                    e.target.closest('.level-row').remove();
                    
                    // Renumber remaining levels
                    updateLevelNumbers();
                });
            });
        }
        
        // Update level numbers
        function updateLevelNumbers() {
            document.querySelectorAll('.level-row').forEach((row, index) => {
                row.querySelector('.level-number').textContent = `Level ${index + 1}`;
                row.querySelector('.remove-btn').dataset.index = index;
            });
        }
        
        // Save tournament data
        function saveTournamentData() {
            const levels = [];
            
            document.querySelectorAll('.level-row').forEach((row, index) => {
                const level = {
                    level: index + 1,
                    small_blind: parseInt(row.querySelector(`input[id^="small-blind-"]`).value),
                    big_blind: parseInt(row.querySelector(`input[id^="big-blind-"]`).value),
                    ante: parseInt(row.querySelector(`input[id^="ante-"]`).value),
                    duration: parseInt(row.querySelector(`input[id^="duration-"]`).value)
                };
                
                levels.push(level);
            });
            
            const updatedTournament = {
                name: tournamentNameInput.value,
                levels: levels
            };
            
            // Send to server
            fetch('/api/tournament', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedTournament)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = '/';
                }
            })
            .catch(error => {
                console.error('Error saving tournament:', error);
                alert('Error saving tournament. Please try again.');
            });
        }
        
        // Event listeners
        addLevelBtn.addEventListener('click', () => {
            addLevelRow({}, document.querySelectorAll('.level-row').length);
            addRemoveListeners();
        });
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            saveTournamentData();
        });
        
        // Initialize
        loadTournamentData();
        addRemoveListeners();
    </script>
</body>
</html>
''')
    
    # Create static CSS
    with open('static/style.css', 'w') as f:
        f.write('''
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Arial', sans-serif;
}

body {
    background-color: #121212;
    color: #ffffff;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    text-align: center;
}

h1 {
    font-size: 2.5rem;
    margin-bottom: 20px;
    color: #4CAF50;
}

h2 {
    font-size: 1.8rem;
    margin-bottom: 10px;
    color: #90CAF9;
}

.btn {
    display: inline-block;
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    margin: 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    text-decoration: none;
    transition: background-color 0.3s;
}

.btn:hover {
    background-color: #45a049;
}

.btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

/* Timer page styles */
.timer-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.timer-display {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
    margin: 20px 0;
    width: 100%;
}

.time-remaining, .current-level, .next-level {
    flex: 1;
    min-width: 300px;
    padding: 20px;
    background-color: #1e1e1e;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.timer {
    font-size: 4rem;
    font-weight: bold;
    margin: 10px 0;
    color: #ffffff;
}

.timer.warning {
    color: #ff5722;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.level-info {
    margin: 10px 0;
}

.level-number {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 10px;
    color: #FFC107;
}

.blinds {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.blind {
    font-size: 1.2rem;
}

.timer-controls {
    margin: 20px 0;
}

.control-btn {
    font-size: 1.2rem;
    min-width: 100px;
}

/* Admin page styles */
.admin-container {
    max-width: 800px;
    text-align: left;
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

input[type="text"],
input[type="number"] {
    width: 100%;
    padding: 10px;
    border: 1px solid #444;
    border-radius: 5px;
    background-color: #333;
    color: white;
    font-size: 1rem;
}

.level-row {
    background-color: #1e1e1e;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}

.level-inputs {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.remove-btn {
    background-color: #f44336;
    grid-column: span 1;
}

.remove-btn:hover {
    background-color: #d32f2f;
}

.form-actions {
    margin-top: 30px;
    display: flex;
    justify-content: center;
    gap: 20px;
}

@media (max-width: 768px) {
    .timer-display {
        flex-direction: column;
    }
    
    .time-remaining, .current-level, .next-level {
        width: 100%;
    }
    
    .timer {
        font-size: 3rem;
    }
    
    .level-inputs {
        grid-template-columns: 1fr;
    }
}
''')
    
    # Create a placeholder sound file
    with open('static/level-up.mp3', 'w') as f:
        f.write('placeholder for sound file')
    
    app.run(debug=True, host='0.0.0.0', port=8080)
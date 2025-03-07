from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "levels": [
        {"level": 1, "small_blind": 5, "big_blind": 10, "duration": 15},
        {"level": 2, "small_blind": 10, "big_blind": 20, "duration": 15},
        {"level": 3, "small_blind": 15, "big_blind": 30, "duration": 15},
        {"level": 4, "small_blind": 25, "big_blind": 50, "duration": 15},
        {"level": 5, "small_blind": 50, "big_blind": 100, "duration": 15},
        {"level": 6, "small_blind": 75, "big_blind": 150, "duration": 15},
        {"level": 7, "small_blind": 100, "big_blind": 200, "duration": 15},
        {"level": 8, "small_blind": 200, "big_blind": 400, "duration": 15},
        {"level": 9, "small_blind": 300, "big_blind": 600, "duration": 15},
        {"level": 10, "small_blind": 500, "big_blind": 1000, "duration": 15}
    ],
    "chips": {
        "white": 1,
        "blue": 5,
        "red": 25,
        "green": 100,
        "black": 500
    }
}

CONFIG_FILE = "poker_config.json"

# Load configuration from file or use default
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

# Save configuration to file
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Main route displays the timer
@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

# Settings page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    config = load_config()
    
    if request.method == 'POST':
        # Process chip values
        chips = {
            "white": int(request.form.get('white_value', 1)),
            "blue": int(request.form.get('blue_value', 5)),
            "red": int(request.form.get('red_value', 25)),
            "green": int(request.form.get('green_value', 100)),
            "black": int(request.form.get('black_value', 500))
        }
        
        # Process levels
        levels = []
        level_count = int(request.form.get('level_count', 10))
        
        for i in range(1, level_count + 1):
            level = {
                "level": i,
                "small_blind": int(request.form.get(f'small_blind_{i}', 0)),
                "big_blind": int(request.form.get(f'big_blind_{i}', 0)),
                "duration": int(request.form.get(f'duration_{i}', 15))
            }
            levels.append(level)
        
        # Save new configuration
        new_config = {
            "levels": levels,
            "chips": chips
        }
        save_config(new_config)
        return redirect(url_for('index'))
    
    return render_template('settings.html', config=config)

# API endpoint to get configuration
@app.route('/api/config')
def get_config():
    return jsonify(load_config())

# API endpoint to update current level
@app.route('/api/set_level/<int:level_id>')
def set_level(level_id):
    config = load_config()
    if 1 <= level_id <= len(config['levels']):
        config['current_level'] = level_id
        save_config(config)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid level ID"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
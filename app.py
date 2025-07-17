from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from game_engine import GameEngine
from player import Player
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Store active games (in production, use a database)
active_games = {}

@app.route('/')
def index():
    """Main landing page - player registration"""
    if 'player_name' in session and 'game_id' in session:
        # Player already registered, redirect to game
        return redirect(url_for('game'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle player registration"""
    player_name = request.form.get('player_name', '').strip()
    
    if not player_name:
        return render_template('index.html', error="Please enter a valid name!")
    
    # Create unique game session
    game_id = str(uuid.uuid4())
    
    # Create player and game engine
    player = Player(player_name)
    game_engine = GameEngine(session_id=game_id)
    
    # Store in session and active games
    session['player_name'] = player_name
    session['game_id'] = game_id
    
    active_games[game_id] = {
        'player': player,
        'game_engine': game_engine
    }
    
    return redirect(url_for('game'))

@app.route('/game')
def game():
    """Main game page"""
    if 'player_name' not in session or 'game_id' not in session:
        return redirect(url_for('index'))
    
    game_id = session['game_id']
    if game_id not in active_games:
        # Game session lost, restart
        session.clear()
        return redirect(url_for('index'))
    
    player = active_games[game_id]['player']
    
    return render_template('game.html', 
                         player_name=player.name,
                         player_stats=player.to_string())

@app.route('/start_game', methods=['POST'])
def start_game():
    """Initialize the game with the first narrative"""
    if 'game_id' not in session or session['game_id'] not in active_games:
        return jsonify({'error': 'No active game session'}), 400
    
    game_data = active_games[session['game_id']]
    player = game_data['player']
    game_engine = game_data['game_engine']
    
    # Start the game with an initial prompt
    initial_prompt = f"The player's name is {player.name}. Begin the adventure by introducing them to a fantasy world. Provide an engaging opening scenario."
    
    try:
        response = game_engine.process_message(player, initial_prompt)
        
        return jsonify({
            'narration': response.narration,
            'choices': response.choices,
            'player_stats': player.to_string()
        })
    except Exception as e:
        return jsonify({'error': f'Game error: {str(e)}'}), 500

@app.route('/take_action', methods=['POST'])
def take_action():
    """Handle player action selection"""
    if 'game_id' not in session or session['game_id'] not in active_games:
        return jsonify({'error': 'No active game session'}), 400
    
    action = request.json.get('action', '').strip()
    if not action:
        return jsonify({'error': 'No action provided'}), 400
    
    game_data = active_games[session['game_id']]
    player = game_data['player']
    game_engine = game_data['game_engine']
    
    try:
        # Process the player's chosen action
        response = game_engine.process_message(player, action)
        
        return jsonify({
            'narration': response.narration,
            'choices': response.choices,
            'player_stats': player.to_string()
        })
    except Exception as e:
        return jsonify({'error': f'Game error: {str(e)}'}), 500

@app.route('/custom_action', methods=['POST'])
def custom_action():
    """Handle custom player input (when they choose 'Other')"""
    if 'game_id' not in session or session['game_id'] not in active_games:
        return jsonify({'error': 'No active game session'}), 400
    
    custom_input = request.json.get('custom_input', '').strip()
    if not custom_input:
        return jsonify({'error': 'No custom input provided'}), 400
    
    game_data = active_games[session['game_id']]
    player = game_data['player']
    game_engine = game_data['game_engine']
    
    try:
        # Process the player's custom input
        response = game_engine.process_message(player, custom_input)
        
        return jsonify({
            'narration': response.narration,
            'choices': response.choices,
            'player_stats': player.to_string()
        })
    except Exception as e:
        return jsonify({'error': f'Game error: {str(e)}'}), 500

@app.route('/logout')
def logout():
    """End the current game session"""
    if 'game_id' in session and session['game_id'] in active_games:
        del active_games[session['game_id']]
    
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

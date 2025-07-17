# 🧙‍♂️ AI RPG Dungeon Master

An interactive web-based RPG game where an AI serves as your Dungeon Master, creating dynamic adventures based on your choices.

## 🌟 Features

- **Web-based Interface**: Beautiful, responsive web UI with Bootstrap styling
- **Player Registration**: Enter your character name to start your adventure
- **AI Dungeon Master**: Powered by Ollama LLM (llama3.2) for dynamic storytelling
- **Interactive Choices**: Click buttons to make decisions or type custom actions
- **Player Stats**: Track HP, attack, defense, level, and inventory
- **Game Actions**: Automatic stat updates based on AI decisions (damage, healing, items, etc.)
- **Session Management**: Each player gets their own game session

## 🎮 Game Flow

1. **Player Registration**: Enter your adventurer name on the landing page
2. **Game Start**: AI DM creates your opening scenario
3. **Adventure Loop**: 
   - Read the AI's narrative description
   - Choose from 3-4 action buttons OR type a custom action
   - AI processes your choice and updates the game world
   - See your stats update in real-time
   - Continue the adventure!

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- llama3.2 model downloaded in Ollama

### Installation

1. **Install Ollama and Model**:
   ```bash
   # Install Ollama from https://ollama.ai/
   # Then pull the model:
   ollama pull llama3.2
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Game**:
   ```bash
   python app.py
   ```
   
   Or on Windows, simply double-click `run_game.bat`

4. **Open Your Browser**:
   Go to `http://localhost:5000`

## 🎯 How to Play

1. **Start**: Enter your character name on the homepage
2. **Begin Adventure**: Click "Start Your Journey" 
3. **Make Choices**: Read the AI's story and click action buttons
4. **Custom Actions**: Choose "Other" to type your own creative actions
5. **Watch Stats**: Your character stats update automatically based on events
6. **Continue**: Keep making choices to drive your unique story forward!

## 🛠️ Technical Details

### File Structure
- `app.py` - Flask web application
- `game_engine.py` - Core game logic and AI integration
- `player.py` - Player character class with stats and inventory
- `action_config.py` - Defines available game actions
- `prompt.py` - AI prompt engineering for the Dungeon Master
- `templates/` - HTML templates for the web interface

### Game Actions
The AI can automatically execute these actions to update your character:
- `@take_damage(amount)` - Reduce player HP
- `@heal_player(amount)` - Restore player HP  
- `@adjust_atk(amount)` - Modify attack stat
- `@adjust_df(amount)` - Modify defense stat
- `@add_item(name, description, consumable)` - Add items to inventory
- `@use_item(name)` - Use items from inventory

### AI Integration
- Uses Ollama with llama3.2 model
- Structured JSON responses from AI
- Message history maintained per session
- Robust error handling and fallbacks

## 🔧 Customization

- **Change AI Model**: Modify the `model` parameter in `GameEngine.__init__()`
- **Add New Actions**: Define new functions in `action_config.py`
- **Modify Prompts**: Edit the prompt templates in `prompt.py`
- **UI Styling**: Customize CSS in the HTML templates

## 🐛 Troubleshooting

- **"Connection Error"**: Make sure Ollama is running (`ollama serve`)
- **"Model Not Found"**: Ensure llama3.2 is installed (`ollama pull llama3.2`)
- **Port 5000 in use**: Change the port in `app.py` 
- **AI Responses Invalid**: Check Ollama logs for model errors

## 🎨 UI Preview

The game features a modern, fantasy-themed interface with:
- Gradient backgrounds and smooth animations
- Player stats sidebar with character information
- Immersive narrative text area
- Interactive action buttons with icons
- Custom action input for creative freedom
- Responsive design for mobile and desktop

Enjoy your AI-powered adventure! 🗡️⚔️🛡️
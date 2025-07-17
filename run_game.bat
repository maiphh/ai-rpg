@echo off
echo Starting AI RPG Dungeon Master Game...
echo.
echo Make sure you have Ollama running with llama3.2 model installed.
echo If not, install Ollama and run: ollama pull llama3.2
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
echo.
echo Starting the Flask application...
echo Open your browser and go to: http://localhost:5000
echo.
python app.py
pause

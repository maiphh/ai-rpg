from typing import List, Tuple, Dict, Any
import re
from action_config import ACTIONS
from player import Player
from game_engine import *

game = GameEngine()
player = Player("Hero")

while True:
    user_input = input("Enter your action: ")

    print(game.process_message(player, user_input))

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from player import *
from action_config import ACTIONS, get_all_actions
from typing import List, Tuple, Dict, Any
import re


llm = ChatOllama(model="llama3.2", temperature=0.7, max_tokens=150, top_p=0.5)
memory = InMemoryChatMessageHistory()

store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

conversation = RunnableWithMessageHistory(
    llm,
    get_session_history,
    # verbose = True,
)



def get_init_prompt():
    return"""
    You are a Dungeon Master for a fantasy role-playing game. 
    Narrate scenes vividly, respond to the player's choices, and guide them through a creative journey.

    CRITICAL: You MUST use game actions frequently to modify the game state. Every interaction should trigger appropriate actions.

    MANDATORY ACTION USAGE EXAMPLES:
    - When player takes damage: @take_damage(amount)
    - When player heals: @heal_player(amount)
    - When player gains experience: @gain_experience(amount)
    - When combat occurs: use appropriate combat actions
    - When player's stats change: use stat modification actions

    Available actions: """ + get_all_actions() + """

    ACTION TRIGGER RULES:
    1. ALWAYS call at least one action per response
    2. Use actions immediately when describing events
    3. Don't just describe - actually modify the game state
    4. Example: "You find a sword @add_item('Iron Sword', 'An Iron Sword', False) and take 5 damage from a trap @take_damage(5)"

    Every response have 3 predefined choices.
    Format choices with:
    1️⃣ Choice one
    2️⃣ Choice two  
    3️⃣ Choice three
    4️⃣ Other (type your own action)

    Debug mode available with option 5.

    Remember: USE ACTIONS TO MAKE CHANGES REAL, not just describe them!

    First, introduce the game world and the player character.
    """

def chat(player: Player, message: str) -> str:
    player_stat = f"\n\nCurrent Player Stats: {player.to_string()}\n"
    message = player_stat + message

    response = conversation.invoke(
        {"input": message},
        config={"configurable": {"session_id": "default"}}
    )

    text, actions = parse_ai_response(response.content)
    
    execute_actions(player, actions)
    return response.content

def parse_ai_response(response: str) -> Tuple[str, List[Tuple[str, List]]]:
    """
    Parse AI response to extract text and action calls.
    """
    actions_found = []
    cleaned_text = response
    
    # Remove markdown escaping from the response first
    response = response.replace('\\_', '_')
    cleaned_text = cleaned_text.replace('\\_', '_')
    
    # Pattern to match @action_name(param1, param2, param3, ...)
    action_pattern = r'@(\w+)\(([^)]*)\)'
    
    for match in re.finditer(action_pattern, response):
        action_name = match.group(1)
        params_str = match.group(2)
        
        # Check if action exists in our ACTIONS config
        if action_name in ACTIONS:
            # Parse parameters into a list
            params = []
            if params_str.strip():
                # Split by comma and parse each parameter
                param_values = [p.strip() for p in params_str.split(',')]
                for value in param_values:
                    # Try to convert to appropriate type
                    try:
                        # Try int first
                        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                            params.append(int(value))
                        # Try float
                        elif '.' in value and value.replace('.', '').replace('-', '').isdigit():
                            params.append(float(value))
                        # Try boolean
                        elif value.lower() in ['true', 'false']:
                            params.append(value.lower() == 'true')
                        # Keep as string
                        else:
                            # Remove quotes if present
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            params.append(value)
                    except ValueError:
                        params.append(value)
            
            actions_found.append((action_name, params))
            # Remove the action call from the text
            cleaned_text = cleaned_text.replace(match.group(0), '')
    
    # Clean up extra whitespace
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text, actions_found

def execute_action(player, action_name, params=None):
    if params is None:
        params = []
    
    if action_name in ACTIONS:
        action = ACTIONS[action_name]
        # Pass player as first argument, then unpack the params list
        return action["func"](player, *params)
    else:
        raise ValueError(f"Unknown action: {action_name}")

def execute_actions(player, actions: List[Tuple[str, List]]):
    """
    Execute a list of actions parsed from the AI response.
    
    Args:
        player: The player object
        actions: List of (action_name, params) tuples
    """
    for action_name, params in actions:
        try:
            result = execute_action(player, action_name, params)
            print(f"Executed action: {action_name} with params {params}, result: {result}")
        except Exception as e:
            print(f"Error executing action {action_name} with params {params}: {e}")
    


def start_game(player: Player):
    print("Game Master: " + chat(player, get_init_prompt()))

def continue_game(player: Player):
    print("Game Master: " + chat(player, input("You: ")))
    print(player.to_string())



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
    return f"""
You are a Dungeon Master narrating a fantasy role-playing game. 
Your job is to immerse the player with vivid descriptions AND to control the game world using special game actions.

---
💡 CRITICAL: Every narrative that causes a game change MUST include a matching `@action(...)`.
You are not just storytelling — you are updating real game state.
---

### Player's stats:
Never include player stats in your narrative.

### ✅ HOW TO USE ACTIONS

Each action must follow this format:  
@action_name(arg1, arg2, ...)

Only use the actions listed below, exactly as shown.  
Do NOT invent new actions. Do NOT change argument formats.

### 🧰 AVAILABLE ACTIONS:
{get_all_actions()}

### ⚠️ RULES (MANDATORY):

- Do **not just describe** the effects — always apply the matching action
- Use the `@action()` **inline or on a new line**, immediately after the event
- Never invent action names or change how parameters are passed
- If an event happens (trap, healing, item found), it MUST include an action call

---

### 📊 Combat Rules:

1. **Player and enemies have stats**:
   - HP: Health Points
   - ATK: Attack
   - DEF: Defense

2. **Damage = Attacker's ATK - Defender's DEF**
   - Example: If player ATK = 12 and enemy DEF = 5 → damage = 7
   - Always ensure damage is >= 0
   - Update HP using @take_damage(amount)

3. You control enemy actions. After player acts, enemy may retaliate. Use @take_damage() accordingly.


### ✅ CHOICE FORMAT:

At the end of each response, offer 3 default numbered choices like:

1️⃣ Open the chest  
2️⃣ Inspect the room  
3️⃣ Leave quietly  
4️⃣ Other (type your own action)

You MUST always show these choices, even if simple.

🚫 DO NOT show internal action commands (like @take_damage) to the player.

✅ Only use internal @actions to update game state behind the scenes.

✅ Present the player with 3 clean, narrative choices in natural language only.

Example (CORRECT):

1️⃣ Attack the goblin  
2️⃣ Try to run away  
3️⃣ Shout a warning to your allies  
4️⃣ Other (type your own action)

NEVER show this (WRONG):

@take_damage(10)  
@adjust_atk(5)  
@use_item("potion")

These are internal — not part of the player's choices!

---

🧙 Start the game by introducing the player to the world and asking for their name.

Remember: every change to the world = action call.
Be consistent, structured, and never break the rules.
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



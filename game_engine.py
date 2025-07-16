from langchain_ollama import ChatOllama
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage 
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from action_config import *
import json
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import re

@dataclass
class GameResponse:
    text: str
    actions: list[str]
    choices: list[str]
    


class GameEngine:
    def __init__(self, model="llama3.2", session_id: str = "default"):
        self.llm = ChatOllama(model=model)
        self.store = {}
        self.conversation = RunnableWithMessageHistory(
            self.llm,
            self.get_session_history,
        )
        self.session_id = session_id
        

    def get_session_history(self) -> InMemoryChatMessageHistory:
        if self.session_id not in self.store:
            self.store[self.session_id] = InMemoryChatMessageHistory()
            self.store[self.session_id].add_message(SystemMessage(self.get_init_prompt()))
        return self.store[self.session_id]
    
    def get_init_prompt(self):
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
🎯 **RESPONSE FORMAT INSTRUCTIONS**:

Your entire reply **must** be a **single JSON object** with exactly three keys:

- "narration": a string with the scene description.
- "actions": a list of strings, each an `@action(...)` command.
- "choices": a list of strings, each a player option.

No additional text. Ensure the JSON is valid.  
Example:

{{
  "narration": "…",
  "actions": ["@take_damage(5)"],
  "choices": ["Option 1","Option 2","Option 3","Other…"]
}}

🧙 Start the game by introducing the player to the world and asking for their name.

Remember: every change to the world = action call.
Be consistent, structured, and never break the rules.
"""
    
    def process_message(self, player, input):
        response = self.conversation.invoke(
            HumanMessage(content=input),
            config={"configurable": {"session_id": self.session_id}}
        )
        game_response = self.parse_response(response.content)
        self.execute_actions(player, game_response.actions)
        return response.content

    def parse_response(self, response: str):
        try:
            # Try to parse the entire response as JSON first
            json_response = json.loads(response)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the response
            # Look for JSON object patterns
            # Try to find a JSON object in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    json_response = json.loads(json_str)
                except json.JSONDecodeError:
                    # If still failing, create a fallback response
                    print(f"Failed to parse JSON, raw response: {response}")
                    return GameResponse(
                        text=response,
                        actions=[],
                        choices=["Continue", "Ask for clarification", "Try again", "Other"]
                    )
            else:
                # No JSON found, create fallback response
                print(f"No JSON found in response: {response}")
                return GameResponse(
                    text=response,
                    actions=[],
                    choices=["Continue", "Ask for clarification", "Try again", "Other"]
                )
        
        # Extract the required fields with fallbacks
        narration = json_response.get("narration", "")
        actions = json_response.get("actions", [])
        choices = json_response.get("choices", ["Continue", "Ask for clarification", "Try again", "Other"])
        
        return GameResponse(
            text=narration,
            actions=actions,
            choices=choices
        )
    
    
    def execute_action(self, player, action_name, params=None):
        if params is None:
            params = []
        
        if action_name in ACTIONS:
            action = ACTIONS[action_name]
            # Pass player as first argument, then unpack the params list
            return action["func"](player, *params)
        else:
            raise ValueError(f"Unknown action: {action_name}")

    def execute_actions(self, player, actions: List[Tuple[str, List]]):
        """
        Execute a list of actions parsed from the AI response.
        
        Args:
            player: The player object
            actions: List of (action_name, params) tuples
        """
        for action_str in actions:
            try:
                action_name, params = self.parse_action(action_str)
                result = self.execute_action(player, action_name, params)
                print(f"Executed action: {action_name} with params {params}, result: {result}")
            except Exception as e:
                print(f"Error executing action {action_name} with params {params}: {e}")

    def parse_action(self, action_str: str) -> Tuple[str, List]:
        """
        Parse action string like '@take_damage(5)' into ('take_damage', [5])
        """
        # Remove @ symbol and extract function name and parameters
        match = re.match(r'@(\w+)\((.*)\)', action_str.strip())
        if not match:
            raise ValueError(f"Invalid action format: {action_str}")
        
        action_name = match.group(1)
        params_str = match.group(2).strip()
        
        # Parse parameters
        params = []
        if params_str:
            # Split by comma and process each parameter
            for param in params_str.split(','):
                param = param.strip()
                # Try to convert to int/float, otherwise keep as string
                try:
                    if '.' in param:
                        params.append(float(param))
                    else:
                        params.append(int(param))
                except ValueError:
                    # Remove quotes if present and keep as string
                    params.append(param.strip('"\''))
        
        return action_name, params


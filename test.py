from typing import List, Tuple, Dict, Any
import re
from action_config import ACTIONS
from player import Player
from main import *

def parse_ai_response(response: str) -> Tuple[str, List[Tuple[str, List]]]:
    """
    Parse AI response to extract text and action calls.
    
    Args:
        response: The AI response string containing text and @action_name(param1, param2, ...) calls
        
    Returns:
        Tuple of (cleaned_text, list_of_actions)
        where list_of_actions contains (action_name, params_list) tuples
    """
    actions_found = []
    cleaned_text = response
    
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


player = Player("test")  # Initialize player globally for use in actions
def execute_action(action_name, params=None):
    if params is None:
        params = []
    
    if action_name in ACTIONS:
        action = ACTIONS[action_name]
        # Pass player as first argument, then unpack the params list
        return action["func"](player, *params)
    else:
        raise ValueError(f"Unknown action: {action_name}")

def execute_actions(actions: List[Tuple[str, List]]):
    """
    Execute a list of actions parsed from the AI response.
    
    Args:
        actions: List of (action_name, params) tuples
    """
    for action_name, params in actions:
        try:
            result = execute_action(action_name, params)
            print(f"Executed action: {action_name} with params {params}, result: {result}")
        except Exception as e:
            print(f"Error executing action {action_name} with params {params}: {e}")
    

# Usage example:
response = "The dragon attacks! @take_damage(25) You find a potion. @heal_player(10) What will you do?"
text, actions = parse_ai_response(response)
print(f"Text: {text}")  # "The dragon attacks! You find a potion. What will you do?"
print(f"Actions: {actions}")  # [('take_damage', [25]), ('heal_player', [10])]

# Execute actions
execute_actions(actions)


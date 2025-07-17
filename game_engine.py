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
from prompt import get_init_prompt

@dataclass
class GameResponse:
    narration: str
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
        
    
    def process_message(self, player, input):
        response = self.conversation.invoke(
            HumanMessage(content=input),
            config={"configurable": {"session_id": self.session_id}}
        )
        game_response = self.parse_response(response.content)
        self.execute_actions(player, game_response.actions)
        return game_response
    


    def get_session_history(self) -> InMemoryChatMessageHistory:
        if self.session_id not in self.store:
            self.store[self.session_id] = InMemoryChatMessageHistory()
            self.store[self.session_id].add_message(SystemMessage(get_init_prompt()))
        return self.store[self.session_id]
    

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
                        narration=response,
                        actions=[],
                        choices=["Continue", "Ask for clarification", "Try again", "Other"]
                    )
            else:
                # No JSON found, create fallback response
                print(f"No JSON found in response: {response}")
                return GameResponse(
                    narration=response,
                    actions=[],
                    choices=["Continue", "Ask for clarification", "Try again", "Other"]
                )
        
        # Extract the required fields with fallbacks
        narration = json_response.get("narration", "")
        actions = json_response.get("actions", [])
        choices = json_response.get("choices", ["Continue", "Ask for clarification", "Try again", "Other"])
        
        return GameResponse(
            narration=narration,
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
            action_name = None
            params = None
            try:
                action_name, params = self.parse_action(action_str)
                result = self.execute_action(player, action_name, params)
                print(f"Executed action: {action_name} with params {params}, result: {result}")
            except Exception as e:
                print(f"Error executing action '{action_str}': {e}")
                if action_name and params:
                    print(f"  - Action name: {action_name}, params: {params}")

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


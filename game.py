from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from player import *
from action_config import ACTIONS
from main import *


llm = ChatOllama(model="mistral")
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

def chat(player: Player, message: str) -> str:
    player_stat = f"\n\nCurrent Player Stats: {player.to_string()}\n"
    message = player_stat + message

    response = conversation.invoke(
        {"input": message},
        config={"configurable": {"session_id": "default"}}
    )
    return response.content

init_prompt = """
You are a Dungeon Master for a fantasy role-playing game. 
Narrate scenes vividly, respond to the player's choices, and guide them through a creative journey. 
Always end your response with a question like "What will you do next?". Give the player number of possible actions to choose from, and allow them to type their choice by number.
Begin by asking the player for their name and describing the environment.
"""

def execute_action(action_name, params=None):
    if params is None:
        params = []
    
    if action_name in ACTIONS:
        action = ACTIONS[action_name]
        # Pass player as first argument, then unpack the params list
        return action["func"](player, *params)
    else:
        raise ValueError(f"Unknown action: {action_name}")
    


def start_game(player: Player):
    print("Game Master: " + chat(player, init_prompt))

def continue_game(player: Player):
    print("Game Master: " + chat(player, input("You: ")))
    print(player.to_string())



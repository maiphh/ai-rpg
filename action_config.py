from player import Player

ACTIONS = {
    "take_damage": {
        "description": "Deal damage to the player",
        "usage": "@take_damage(amount:int)",
        "example": "@take_damage(20)",
        "trigger": "when something damages the player",
        "func": Player.take_damage,
    },

    "heal_player": {
        "description": "Heal the player",
        "usage": "@heal_player(amount:int)",
        "example": "@heal_player(10)",
        "trigger": "when the player finds a healing item or any blessing that restores health",
        "func": Player.heal,
    },

    "adjust_atk": {
        "description": "Adjust player's attack",
        "usage": "@adjust_atk(amount:int)",
        "example": "@adjust_atk(5)",
        "trigger": "when the player finds a weapon or any item that boosts attack",
        "func": Player.adjust_atk,
    },

    "adjust_df": {
        "description": "Adjust player's defense",
        "usage": "@adjust_df(amount:int)",
        "example": "@adjust_df(3)",
        "trigger": "when the player finds armor or any item that boosts defense",
        "func": Player.adjust_df,
    },

    "add_item": {
        "description": "Add an item to player's inventory",
        "usage": "@add_item(item_name:str, item_description:str, is_consumable:bool=False)",
        "example": "@add_item('Health Potion', 'Restores 20 HP', False)",
        "trigger": "when the player finds an item in the game world, or when npc gives it to them, or any other way of acquiring items",
        "func": Player.add_item,
    },

    "use_item": {
        "description": "Use an item from player's inventory",
        "usage": "@use_item(item_name:str)",
        "example": "@use_item('Health Potion')",
        "trigger": "when the player uses an item from their inventory",
        "func": Player.use_item,
    },

}

def get_all_actions():
    return "\n".join(f"{key}: {value}" for key, value in ACTIONS.items())

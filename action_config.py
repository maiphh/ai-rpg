from player import Player

ACTIONS = {
    "take_damage": {
        "description": "Deal damage to the player",
        "usage": "@take_damage(amount:int)",
        "func": Player.take_damage,
    },

    "heal_player": {
        "description": "Heal the player",
        "usage": "@heal_player(amount:int)",
        "func": Player.heal,
    }
}
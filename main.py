from player import Player
from game import start_game, continue_game

def main():
    player_name = input("Enter your character's name: ")
    global player
    player = Player(name=player_name)
    
    start_game(player)
    
    while True:
        continue_game(player)
        if player.hp <= 0:
            print("Game Over! Your character has fallen.")
            break

if __name__ == "__main__":
    main()

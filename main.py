from game_logic import GameLogic
from data_manager import DataManager

def main():
    game = GameLogic()
    wrestler_data = DataManager.load_wrestlers()
    game.load_wrestlers(wrestler_data)

    # For testing purposes, let's create a match between the first two wrestlers
    if len(game.wrestlers) >= 2:
        match = game.create_match(game.wrestlers[0], game.wrestlers[1])
        result = game.run_match(match)
        print(result)
    else:
        print("Not enough wrestlers to create a match.")

if __name__ == "__main__":
    main()
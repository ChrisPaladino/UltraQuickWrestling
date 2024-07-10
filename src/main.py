import os
from data_manager import DataManager
from game_logic import GameLogic

def get_match_type(game_logic):
    print("Select Match Type:")
    for i, match_type in enumerate(game_logic.match_types, 1):
        print(f"  {i} - {match_type}")
    
    while True:
        try:
            choice = int(input("> "))
            if 1 <= choice <= len(game_logic.match_types):
                return game_logic.match_types[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

def main():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_manager = DataManager(base_path)
    game_logic = GameLogic(data_manager)

    print("Welcome to Ultra Quick Wrestling!")
    
    wrestler1_name = input("Enter name of first wrestler: ")
    wrestler2_name = input("Enter name of second wrestler: ")
    
    match_type = get_match_type(game_logic)
    
    match = game_logic.create_match(wrestler1_name, wrestler2_name, match_type)
    
    if match:
        modifier = game_logic.get_match_modifier()
        print(f"Match modifier: {modifier}")
        game_logic.apply_match_modifier(match, modifier)
        
        result = game_logic.run_match(match)
        print(result)
    else:
        print("One or both wrestlers not found.")

if __name__ == "__main__":
    main()
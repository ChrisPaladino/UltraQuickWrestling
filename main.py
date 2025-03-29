import random
from engine import data_loader
from engine.match import Match

def choose_wrestler(wrestlers, prompt):
    print(f"\n{prompt}")
    for i, w in enumerate(wrestlers):
        print(f"{i+1}. {w['name']} ({w['persona']})")
    while True:
        try:
            choice = int(input("Enter number: "))
            if 1 <= choice <= len(wrestlers):
                return wrestlers[choice - 1]
        except ValueError:
            pass
        print("Invalid choice. Try again.")

def choose_match_type(game_data):
    match_types = list(game_data["win_charts"].keys())
    print("\nChoose Match Type:")
    for i, mt in enumerate(match_types):
        print(f"{i+1}. {mt}")
    while True:
        try:
            choice = int(input("Enter number: "))
            if 1 <= choice <= len(match_types):
                return match_types[choice - 1]
        except ValueError:
            pass
        print("Invalid choice. Try again.")

def main():
    wrestlers = data_loader.load_wrestlers()
    game_data = data_loader.load_game_data()

    print("Welcome to Ultra Quick Wrestling!")

    wrestler_a = choose_wrestler(wrestlers, "Select Wrestler A")
    wrestler_b = choose_wrestler(wrestlers, "Select Wrestler B")

    match_type = choose_match_type(game_data)

    match = Match(wrestler_a, wrestler_b, match_type, game_data)
    print("\n--- MATCH RESULT ---")
    print(match.simulate())

if __name__ == "__main__":
    main()

from engine import data_loader
from engine.match import create_match

def choose_wrestler(wrestlers, role):
    print(f"\nSelect {role.upper()}:")
    for i, w in enumerate(wrestlers):
        print(f"{i + 1}. {w['name']} ({w['persona']})")
    while True:
        choice = input("Enter number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(wrestlers):
            return wrestlers[int(choice) - 1]
        print("Invalid selection. Try again.")

def choose_match_type(game_data):
    print("\nChoose Match Type:")
    types = list(game_data['win_charts'].keys())
    for i, m in enumerate(types):
        print(f"{i + 1}. {m}")
    while True:
        choice = input("Enter number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(types):
            return types[int(choice) - 1]
        print("Invalid selection. Try again.")

def main():
    wrestlers = data_loader.load_wrestlers()
    game_data = data_loader.load_game_data()

    wrestler1 = choose_wrestler(wrestlers, "Wrestler 1")
    wrestler2 = choose_wrestler(wrestlers, "Wrestler 2")

    if wrestler1['persona'] == wrestler2['persona']:
        print("\nBoth wrestlers have the same persona.")
        print("Please assign one as the FACE:")
        print(f"1. {wrestler1['name']}\n2. {wrestler2['name']}")
        while True:
            choice = input("Enter number for who should be FACE: ")
            if choice == '1':
                assigned_roles = {"Face": wrestler1['name'], "Heel": wrestler2['name']}
                break
            elif choice == '2':
                assigned_roles = {"Face": wrestler2['name'], "Heel": wrestler1['name']}
                break
            print("Invalid input. Please enter 1 or 2.")
    else:
        face = wrestler1 if wrestler1['persona'] == "Face" else wrestler2
        heel = wrestler2 if face == wrestler1 else wrestler1
        assigned_roles = {"Face": face['name'], "Heel": heel['name']}

    match_type = choose_match_type(game_data)

    match = create_match(wrestler1, wrestler2, match_type, game_data, assigned_roles)
    print("\n--- MATCH RESULT ---")
    print(match.simulate())

if __name__ == "__main__":
    main()

import argparse
import json
from typing import List, Optional, Sequence, Tuple

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


def _parse_identifier_list(raw_value) -> List[str]:
    if raw_value is None:
        return []

    if isinstance(raw_value, list):
        identifiers = raw_value
    else:
        try:
            parsed = json.loads(raw_value)
            identifiers = parsed if isinstance(parsed, list) else [raw_value]
        except json.JSONDecodeError:
            identifiers = [part.strip() for part in str(raw_value).split(",")]

    return [str(item).strip() for item in identifiers if str(item).strip()]


def _lookup_team(wrestlers: Sequence[dict], identifiers: List[str]) -> List[dict]:
    resolved = []
    missing = []
    for identifier in identifiers:
        match = next((w for w in wrestlers if w.get("name", "").lower() == identifier.lower()), None)
        if match:
            resolved.append(match)
        else:
            missing.append(identifier)

    if missing:
        raise ValueError(f"Unknown wrestler identifiers: {', '.join(missing)}")

    return resolved


def _default_match_type(game_data: dict, *, is_tag: bool = False) -> str:
    win_charts = {}
    if is_tag:
        win_charts = game_data.get("tag_win_charts") or {}
    if not win_charts:
        win_charts = game_data.get("win_charts") or {}
    if not win_charts:
        raise ValueError("No match types available in game data")
    return next(iter(win_charts))


def _resolve_alignment(team_a: Sequence[dict], team_b: Sequence[dict], *, is_tag: bool, preferred_face: Optional[str] = None) -> Tuple[Sequence[dict], Sequence[dict], dict]:
    preferred_upper = preferred_face.upper() if isinstance(preferred_face, str) else None
    if preferred_upper == "A":
        face, heel = team_a, team_b
    elif preferred_upper == "B":
        face, heel = team_b, team_a
    else:
        if is_tag:
            a_is_face = all(member.get("persona") == "Face" for member in team_a)
            b_is_heel = all(member.get("persona") == "Heel" for member in team_b)
            b_is_face = all(member.get("persona") == "Face" for member in team_b)
            a_is_heel = all(member.get("persona") == "Heel" for member in team_a)

            if a_is_face and b_is_heel:
                face, heel = team_a, team_b
            elif b_is_face and a_is_heel:
                face, heel = team_b, team_a
            else:
                raise ValueError("Cannot automatically determine Face/Heel teams. Use --face-team to choose A or B.")
        else:
            persona_a = (team_a[0].get("persona") or "").lower()
            persona_b = (team_b[0].get("persona") or "").lower()
            if persona_a != persona_b:
                face, heel = (team_a, team_b) if persona_a == "face" else (team_b, team_a)
            else:
                raise ValueError("Both wrestlers share the same persona. Use --face-team to choose who is the Face.")

    assigned_roles = {"Face": [member.get("name") for member in face], "Heel": [member.get("name") for member in heel]}
    return face, heel, assigned_roles


def _build_match_from_args(args, wrestlers: Sequence[dict], game_data: dict):
    team_a_ids = _parse_identifier_list(args.team_a)
    team_b_ids = _parse_identifier_list(args.team_b)

    if not team_a_ids or not team_b_ids:
        raise ValueError("Both --team-a and --team-b are required when providing CLI inputs.")

    is_tag = bool(args.tag)
    if not is_tag and (len(team_a_ids) != 1 or len(team_b_ids) != 1):
        raise ValueError("Singles matches require exactly one identifier per side. Use --tag for tag matches.")

    team_a = _lookup_team(wrestlers, team_a_ids)
    team_b = _lookup_team(wrestlers, team_b_ids)
    face_team, heel_team, assigned_roles = _resolve_alignment(team_a, team_b, is_tag=is_tag, preferred_face=args.face_team)

    match_type = args.match_type or _default_match_type(game_data, is_tag=is_tag)
    available_types = set((game_data.get("win_charts") or {}).keys())
    if is_tag:
        available_types.update((game_data.get("tag_win_charts") or {}).keys())
    if match_type not in available_types:
        raise ValueError(f"Unknown match type '{match_type}'. Available types: {', '.join(sorted(available_types))}")

    return create_match(face_team, heel_team, match_type, game_data, assigned_roles=assigned_roles, tag_match=is_tag)


def _build_argument_parser():
    parser = argparse.ArgumentParser(
        description="Simulate Ultra Quick Wrestling matches via CLI or interactive prompts.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--team-a", help="Comma-separated list or JSON array of wrestler names for Team A.")
    parser.add_argument("--team-b", help="Comma-separated list or JSON array of wrestler names for Team B.")
    parser.add_argument("--tag", action="store_true", help="Enable tag match mode (teams can have multiple members).")
    parser.add_argument("--face-team", choices=["A", "B"], help="Explicitly choose which team is the Face side.")
    parser.add_argument("--match-type", help="Match type name (defaults to the first available type).")
    return parser

def main():
    parser = _build_argument_parser()
    args = parser.parse_args()

    wrestlers = data_loader.load_wrestlers()
    game_data = data_loader.load_game_data()

    if args.team_a or args.team_b:
        if not args.team_a or not args.team_b:
            parser.error("Both --team-a and --team-b are required when using CLI inputs.")

        try:
            match = _build_match_from_args(args, wrestlers, game_data)
        except ValueError as exc:
            parser.error(str(exc))
    else:
        wrestler1 = choose_wrestler(wrestlers, "Wrestler 1")
        wrestler2 = choose_wrestler(wrestlers, "Wrestler 2")

        if wrestler1['persona'] == wrestler2['persona']:
            print("\nBoth wrestlers have the same persona.")
            print("Please assign one as the FACE:")
            print(f"1. {wrestler1['name']}\n2. {wrestler2['name']}")
            while True:
                choice = input("Enter number for who should be FACE: ")
                if choice == '1':
                    assigned_roles = {"Face": [wrestler1['name']], "Heel": [wrestler2['name']]}
                    break
                elif choice == '2':
                    assigned_roles = {"Face": [wrestler2['name']], "Heel": [wrestler1['name']]}
                    break
                print("Invalid input. Please enter 1 or 2.")
        else:
            face = wrestler1 if wrestler1['persona'] == "Face" else wrestler2
            heel = wrestler2 if face == wrestler1 else wrestler1
            assigned_roles = {"Face": [face['name']], "Heel": [heel['name']]}

        match_type = choose_match_type(game_data)
        match = create_match(wrestler1, wrestler2, match_type, game_data, assigned_roles)

    print("\n--- MATCH RESULT ---")
    print(match.simulate())

if __name__ == "__main__":
    main()

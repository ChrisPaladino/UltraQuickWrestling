import argparse
import json
from datetime import datetime
from typing import Any, List, Optional, Sequence, Tuple, cast

from src.engine import booking
from src.engine import repository
from src.engine.match import create_match

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


def _parse_belt_list(raw_value) -> List[str]:
    belts = _parse_identifier_list(raw_value)
    return [belt for belt in belts if belt]


def _build_booking_context(args, assigned_roles: dict, match_type: str) -> booking.MatchBookingContext | None:
    event_name = getattr(args, "event_name", None)
    storyline_id = getattr(args, "storyline_id", None)
    belts = _parse_belt_list(getattr(args, "belts", None))
    if not event_name and not storyline_id and not belts:
        return None

    state = booking.load_state()
    event_id = None
    match_id = None
    if event_name:
        normalized = event_name.lower()
        events_list = cast(List[dict], state.get("events", []))
        raw_event = next((e for e in events_list if e.get("name", "").lower() == normalized), None)
        if raw_event:
            event = booking.EventCard.from_dict(raw_event)
        else:
            event = booking.EventCard(
                name=event_name,
                date=getattr(args, "event_date", None) or datetime.utcnow().strftime("%Y-%m-%d"),
                venue=getattr(args, "event_venue", "") or "",
            )
            booking.upsert_event(event)
        event_id = event.id
        card_match = booking.CardMatch(
            match_type=match_type,
            face_side=assigned_roles.get("Face", []),
            heel_side=assigned_roles.get("Heel", []),
            belts=belts,
            storyline_id=storyline_id,
        )
        booking.add_match_to_event(event_id, card_match)
        match_id = card_match.id

    return booking.MatchBookingContext(event_id=event_id, match_id=match_id, storyline_id=storyline_id, belts=belts)


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

    booking_context = _build_booking_context(args, assigned_roles, match_type)
    return create_match(
        face_team, heel_team, match_type, game_data, assigned_roles=assigned_roles, tag_match=is_tag, booking_context=booking_context
    )


def _build_argument_parser():
    parser = argparse.ArgumentParser(
        description="Simulate Ultra Quick Wrestling matches via CLI or interactive prompts, or manage rosters and belts.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--team-a", help="Comma-separated list or JSON array of wrestler names for Team A.")
    parser.add_argument("--team-b", help="Comma-separated list or JSON array of wrestler names for Team B.")
    parser.add_argument("--tag", action="store_true", help="Enable tag match mode (teams can have multiple members).")
    parser.add_argument("--face-team", choices=["A", "B"], help="Explicitly choose which team is the Face side.")
    parser.add_argument("--match-type", help="Match type name (defaults to the first available type).")

    subparsers = parser.add_subparsers(dest="command")

    wrestler_parser = subparsers.add_parser("wrestler", help="Create, update, or delete wrestlers.")
    wrestler_action = wrestler_parser.add_mutually_exclusive_group(required=True)
    wrestler_action.add_argument("--add", action="store_true", help="Create a new wrestler.")
    wrestler_action.add_argument("--update", action="store_true", help="Update an existing wrestler.")
    wrestler_action.add_argument("--delete", action="store_true", help="Delete a wrestler.")
    wrestler_parser.add_argument("--name", required=True, help="Wrestler name.")
    wrestler_parser.add_argument("--persona", choices=["Face", "Heel"], help="Persona (Face or Heel).")
    wrestler_parser.add_argument("--finisher", help="Finisher name.")
    wrestler_parser.add_argument("--overall", type=int, help="Overall rating (integer).")

    belt_parser = subparsers.add_parser("belt", help="Assign title belts.")
    belt_parser.add_argument("--assign", action="store_true", help="Assign the belt to the holder.")
    belt_parser.add_argument("--belt", required=True, help="Belt name.")
    belt_parser.add_argument("--holder", required=True, help="Wrestler name to hold the belt.")

    event_parser = subparsers.add_parser("event", help="Schedule an event.")
    event_parser.add_argument("--name", required=True, help="Event name.")
    event_parser.add_argument("--date", help="Optional date string.")
    event_parser.add_argument("--location", help="Optional location description.")
    event_parser.add_argument("--details", help="Additional JSON payload to merge into the event.")
    parser.add_argument("--event-name", help="Optional event name to attach the simulated match to.")
    parser.add_argument("--event-date", help="Event date when logging a match outcome.")
    parser.add_argument("--event-venue", help="Venue name when logging a match outcome.")
    parser.add_argument("--storyline-id", help="Attach the match to an existing storyline id for booking timeline tracking.")
    parser.add_argument("--belts", help="Comma-separated or JSON array of belts on the line.")
    return parser

def main():
    parser = _build_argument_parser()
    args = parser.parse_args()

    if args.command == "wrestler":
        try:
            if args.add:
                payload = {
                    "name": args.name,
                    "persona": args.persona or "Face",
                    "finisher": args.finisher or "",
                    "overall": args.overall if args.overall is not None else 1000,
                }
                repository.create_wrestler(payload)
                print(f"Created wrestler '{args.name}'.")
            elif args.update:
                updates = {}
                if args.persona:
                    updates["persona"] = args.persona
                if args.finisher is not None:
                    updates["finisher"] = args.finisher
                if args.overall is not None:
                    updates["overall"] = args.overall
                repository.update_wrestler(args.name, updates)
                print(f"Updated wrestler '{args.name}'.")
            elif args.delete:
                repository.delete_wrestler(args.name)
                print(f"Deleted wrestler '{args.name}'.")
        except ValueError as exc:
            parser.error(str(exc))
        return

    if args.command == "belt":
        if not args.assign:
            parser.error("Currently only belt assignment is supported (use --assign).")
        try:
            repository.assign_belt(args.belt, args.holder)
            print(f"Assigned '{args.belt}' to '{args.holder}'.")
        except ValueError as exc:
            parser.error(str(exc))
        return

    if args.command == "event":
        event = {"name": args.name}
        if args.date:
            event["date"] = args.date
        if args.location:
            event["location"] = args.location
        if args.details:
            try:
                parsed_details = json.loads(args.details)
                if isinstance(parsed_details, dict):
                    event.update(parsed_details)
            except json.JSONDecodeError as exc:
                parser.error(f"Invalid JSON for --details: {exc}")

        try:
            repository.schedule_event(event)
            print(f"Scheduled event '{args.name}'.")
        except ValueError as exc:
            parser.error(str(exc))
        return

    wrestlers = repository.load_wrestlers()
    game_data = repository.load_game_data()

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

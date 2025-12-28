"""Data access layer for Ultra Quick Wrestling.

This module centralizes reading and writing roster data while ensuring
durable, validated saves. All writes go through :func:`safe_write_json` so the
data files are replaced atomically, preventing corruption from partial writes.
"""

from __future__ import annotations

import json
from pathlib import Path
import uuid
from typing import Any, Dict, List, Tuple

from engine.file_utils import safe_write_json
from engine.game_data import normalize_game_data


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def data_path(filename: str) -> Path:
    return DATA_DIR / filename


def _read_json(filename: str, *, default: Dict[str, Any] | None = None, required: bool = False) -> Dict[str, Any]:
    filepath = data_path(filename)
    if not filepath.exists():
        if required:
            raise FileNotFoundError(f"Missing required data file: {filepath}")
        return default or {}

    with open(filepath, "r") as handle:
        return json.load(handle)


def load_wrestlers() -> List[dict]:
    data = _read_json("wrestlers.json", default={"wrestlers": []})
    return data.get("wrestlers", [])


def load_belts() -> List[dict]:
    data = _read_json("belts.json", default={"belts": []})
    return data.get("belts", [])


def load_booking_state() -> Dict[str, Any]:
    data = _read_json("events.json", default={"events": [], "storylines": [], "timeline": []})
    data.setdefault("events", [])
    data.setdefault("storylines", [])
    data.setdefault("timeline", [])
    return data


def load_events() -> List[dict]:
    state = load_booking_state()
    return state.get("events", [])


def load_game_data() -> Dict[str, Any]:
    raw_data = _read_json("game_data.json", required=True)
    return normalize_game_data(raw_data)


def save_wrestlers(wrestlers: List[dict]) -> None:
    payload = {"wrestlers": wrestlers}
    safe_write_json(str(data_path("wrestlers.json")), payload)


def save_belts(belts: List[dict]) -> None:
    payload = {"belts": belts}
    safe_write_json(str(data_path("belts.json")), payload)


def save_booking_state(state: Dict[str, Any]) -> None:
    payload = {
        "events": state.get("events", []),
        "storylines": state.get("storylines", []),
        "timeline": state.get("timeline", []),
    }
    safe_write_json(str(data_path("events.json")), payload)


def save_events(events: List[dict]) -> None:
    payload = load_booking_state()
    payload["events"] = events
    save_booking_state(payload)


def _find_by_name(items: List[dict], name: str) -> Tuple[int, dict]:
    for index, item in enumerate(items):
        if item.get("name", "").lower() == name.lower():
            return index, item
    raise ValueError(f"Item named '{name}' does not exist.")


def create_wrestler(wrestler: Dict[str, Any]) -> Dict[str, Any]:
    name = (wrestler or {}).get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Wrestler must include a non-empty 'name'.")

    wrestlers = load_wrestlers()
    if any(existing.get("name", "").lower() == name.lower() for existing in wrestlers):
        raise ValueError(f"Wrestler named '{name}' already exists.")

    wrestlers.append(wrestler)
    save_wrestlers(wrestlers)
    return wrestler


def update_wrestler(name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    if not updates:
        raise ValueError("No updates provided for wrestler.")

    wrestlers = load_wrestlers()
    index, wrestler = _find_by_name(wrestlers, name)

    new_name = updates.get("name", wrestler.get("name"))
    if not isinstance(new_name, str) or not new_name.strip():
        raise ValueError("Updated wrestler name must be a non-empty string.")

    normalized_new = new_name.lower()
    for existing in wrestlers:
        if existing is wrestler:
            continue
        if existing.get("name", "").lower() == normalized_new:
            raise ValueError(f"Another wrestler already uses the name '{new_name}'.")

    updated = {**wrestler, **updates, "name": new_name}
    wrestlers[index] = updated
    save_wrestlers(wrestlers)
    return updated


def delete_wrestler(name: str) -> None:
    wrestlers = load_wrestlers()
    new_roster = [w for w in wrestlers if w.get("name", "").lower() != name.lower()]
    if len(new_roster) == len(wrestlers):
        raise ValueError(f"Wrestler named '{name}' does not exist.")

    save_wrestlers(new_roster)


def delete_belt(name: str) -> None:
    belts = load_belts()
    new_belts = [b for b in belts if b.get("name", "").lower() != name.lower()]
    if len(new_belts) == len(belts):
        raise ValueError(f"Belt named '{name}' does not exist.")

    save_belts(new_belts)


def assign_belt(belt_name: str, holder_name: str) -> Dict[str, Any]:
    wrestlers = load_wrestlers()
    if not any(w.get("name", "").lower() == holder_name.lower() for w in wrestlers):
        raise ValueError(f"Cannot assign belt to unknown wrestler '{holder_name}'.")

    belts = load_belts()
    index, belt = _find_by_name(belts, belt_name)

    updated = {**belt, "current_holder": holder_name}
    belts[index] = updated
    save_belts(belts)
    return updated


def schedule_event(event: Dict[str, Any]) -> Dict[str, Any]:
    name = (event or {}).get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Event must include a non-empty 'name'.")

    event = {**event}
    event.setdefault("id", f"event-{uuid.uuid4().hex[:8]}")
    state = load_booking_state()
    events = state.get("events", [])
    events.append(event)
    state["events"] = events
    save_booking_state(state)
    return event

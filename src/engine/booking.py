from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from . import repository


def _default_date() -> str:
    """Return an ISO-ish date string for timeline stamps."""
    return datetime.utcnow().strftime("%Y-%m-%d")


def _generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@dataclass
class StoryBeat:
    """Represents a single moment in a storyline (e.g., run-in, promo, reveal)."""

    summary: str
    occurred_on: str = field(default_factory=_default_date)

    def to_dict(self) -> Dict[str, str]:
        return {"summary": self.summary, "occurred_on": self.occurred_on}

    @classmethod
    def from_dict(cls, payload: Dict[str, str]) -> "StoryBeat":
        return cls(summary=payload.get("summary", ""), occurred_on=payload.get("occurred_on", _default_date()))


@dataclass
class Storyline:
    """Tracks an ongoing feud/rivalry between wrestlers or teams."""

    name: str
    participants: List[str]
    id: str = field(default_factory=lambda: _generate_id("feud"))
    beats: List[StoryBeat] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "participants": self.participants,
            "beats": [beat.to_dict() for beat in self.beats],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Storyline":
        beats = [StoryBeat.from_dict(entry) for entry in payload.get("beats", [])]
        return cls(
            id=payload.get("id") or _generate_id("feud"),
            name=payload.get("name", "Storyline"),
            participants=list(payload.get("participants", [])),
            beats=beats,
        )


@dataclass
class CardMatch:
    """Describes a booked match on an event card."""

    match_type: str
    face_side: List[str]
    heel_side: List[str]
    belts: List[str] = field(default_factory=list)
    storyline_id: Optional[str] = None
    id: str = field(default_factory=lambda: _generate_id("match"))

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "match_type": self.match_type,
            "face_side": self.face_side,
            "heel_side": self.heel_side,
            "belts": self.belts,
            "storyline_id": self.storyline_id,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "CardMatch":
        return cls(
            id=payload.get("id") or _generate_id("match"),
            match_type=payload.get("match_type", ""),
            face_side=list(payload.get("face_side", [])),
            heel_side=list(payload.get("heel_side", [])),
            belts=list(payload.get("belts", [])),
            storyline_id=payload.get("storyline_id"),
        )


@dataclass
class EventCard:
    """Represents a scheduled show containing multiple matches."""

    name: str
    date: str
    venue: str
    notes: str = ""
    matches: List[CardMatch] = field(default_factory=list)
    id: str = field(default_factory=lambda: _generate_id("event"))

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "date": self.date,
            "venue": self.venue,
            "notes": self.notes,
            "matches": [m.to_dict() for m in self.matches],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "EventCard":
        matches = [CardMatch.from_dict(m) for m in payload.get("matches", [])]
        return cls(
            id=payload.get("id") or _generate_id("event"),
            name=payload.get("name", "Event"),
            date=payload.get("date", _default_date()),
            venue=payload.get("venue", ""),
            notes=payload.get("notes", ""),
            matches=matches,
        )


@dataclass
class TimelineEntry:
    """A normalized record of a match outcome for later display."""

    event_id: Optional[str]
    match_id: Optional[str]
    storyline_id: Optional[str]
    match_type: str
    winner: List[str]
    loser: List[str]
    belts: List[str]
    post_result: str
    log: str
    notes: str = ""
    occurred_on: str = field(default_factory=_default_date)

    def to_dict(self) -> Dict[str, object]:
        return {
            "event_id": self.event_id,
            "match_id": self.match_id,
            "storyline_id": self.storyline_id,
            "match_type": self.match_type,
            "winner": self.winner,
            "loser": self.loser,
            "belts": self.belts,
            "post_result": self.post_result,
            "log": self.log,
            "notes": self.notes,
            "occurred_on": self.occurred_on,
        }


def load_state() -> Dict[str, object]:
    """Load booking state from disk with defaults."""
    return repository.load_booking_state()


def save_state(state: Dict[str, object]) -> None:
    repository.save_booking_state(state)


def upsert_storyline(storyline: Storyline) -> Storyline:
    state = load_state()
    storylines = state.get("storylines", [])
    storylines = [s for s in storylines if s.get("id") != storyline.id]
    storylines.append(storyline.to_dict())
    state["storylines"] = storylines
    save_state(state)
    return storyline


def upsert_event(event: EventCard) -> EventCard:
    state = load_state()
    events = state.get("events", [])
    events = [e for e in events if e.get("id") != event.id]
    events.append(event.to_dict())
    state["events"] = events
    save_state(state)
    return event


def add_match_to_event(event_id: str, card_match: CardMatch) -> CardMatch:
    state = load_state()
    updated_events = []
    found = False
    for raw_event in state.get("events", []):
        if raw_event.get("id") == event_id:
            event = EventCard.from_dict(raw_event)
            event.matches.append(card_match)
            updated_events.append(event.to_dict())
            found = True
        else:
            updated_events.append(raw_event)
    if not found:
        raise ValueError(f"Event with id '{event_id}' not found.")
    state["events"] = updated_events
    save_state(state)
    return card_match


def update_match_in_event(event_id: str, updated_match: CardMatch) -> CardMatch:
    state = load_state()
    updated_events = []
    found_event = False
    updated = False
    for raw_event in state.get("events", []):
        if raw_event.get("id") == event_id:
            found_event = True
            event = EventCard.from_dict(raw_event)
            new_matches = []
            for match in event.matches:
                if match.id == updated_match.id:
                    new_matches.append(updated_match)
                    updated = True
                else:
                    new_matches.append(match)
            if not updated:
                raise ValueError(f"Match with id '{updated_match.id}' not found on event '{event_id}'.")
            event.matches = new_matches
            updated_events.append(event.to_dict())
        else:
            updated_events.append(raw_event)
    if not found_event:
        raise ValueError(f"Event with id '{event_id}' not found.")
    state["events"] = updated_events
    save_state(state)
    return updated_match


def remove_match_from_event(event_id: str, match_id: str) -> None:
    state = load_state()
    updated_events = []
    found_event = False
    for raw_event in state.get("events", []):
        if raw_event.get("id") == event_id:
            found_event = True
            event = EventCard.from_dict(raw_event)
            event.matches = [m for m in event.matches if m.id != match_id]
            updated_events.append(event.to_dict())
        else:
            updated_events.append(raw_event)
    if not found_event:
        raise ValueError(f"Event with id '{event_id}' not found.")
    state["events"] = updated_events
    save_state(state)


def update_event(event_id: str, *, name: str, date: str, venue: str, notes: str = "") -> EventCard:
    state = load_state()
    updated_events = []
    updated_card: EventCard | None = None
    for raw_event in state.get("events", []):
        if raw_event.get("id") == event_id:
            card = EventCard.from_dict(raw_event)
            card.name = name
            card.date = date
            card.venue = venue
            card.notes = notes
            updated_card = card
            updated_events.append(card.to_dict())
        else:
            updated_events.append(raw_event)
    if updated_card is None:
        raise ValueError(f"Event with id '{event_id}' not found.")
    state["events"] = updated_events
    save_state(state)
    return updated_card


def record_timeline_entry(entry: TimelineEntry) -> TimelineEntry:
    state = load_state()
    timeline = state.get("timeline", [])
    timeline.append(entry.to_dict())
    state["timeline"] = timeline
    save_state(state)
    return entry


def update_timeline_entry(index: int, updates: Dict[str, object]) -> Dict[str, object]:
    state = load_state()
    timeline = state.get("timeline", [])
    if index < 0 or index >= len(timeline):
        raise IndexError(f"Timeline entry index {index} is out of range.")
    entry = {**timeline[index], **updates}
    timeline[index] = entry
    state["timeline"] = timeline
    save_state(state)
    return entry


@dataclass
class MatchBookingContext:
    """Context passed into match simulation to persist results."""

    event_id: Optional[str] = None
    match_id: Optional[str] = None
    storyline_id: Optional[str] = None
    belts: List[str] = field(default_factory=list)

    def record_outcome(self, *, winner: List[str], loser: List[str], post_result: str, log: str, match_type: str) -> None:
        entry = TimelineEntry(
            event_id=self.event_id,
            match_id=self.match_id,
            storyline_id=self.storyline_id,
            match_type=match_type,
            winner=winner,
            loser=loser,
            belts=self.belts,
            post_result=post_result,
            log=log,
        )
        record_timeline_entry(entry)

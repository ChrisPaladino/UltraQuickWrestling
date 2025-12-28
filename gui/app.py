import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine import booking, repository
from engine.advanced_rules import AdvancedRulesConfig
from engine.match import create_match


class DataStore:
    def __init__(self):
        self.reload()

    def reload(self):
        self.wrestlers = repository.load_wrestlers()
        self.belts = repository.load_belts()
        self.game_data = repository.load_game_data()
        self.booking_state = booking.load_state()
        self.events = self.booking_state.get("events", [])
        self.storylines = self.booking_state.get("storylines", [])
        self.timeline = self.booking_state.get("timeline", [])

    def wrestler_names(self):
        return sorted([w.get("name", "") for w in self.wrestlers], key=lambda name: name.lower())

    def wrestler_display_labels(self):
        labels = []
        for w in self.wrestlers:
            name = w.get("name", "")
            persona = w.get("persona", "Face")
            overall = w.get("overall", 0)
            labels.append((f"{name} ({persona[0] if persona else '?'} / {overall})", name))
        labels.sort(key=lambda pair: pair[1].lower())
        return labels

    def belt_names(self):
        return [b.get("name", "") for b in self.belts]

    def event_names(self):
        return [e.get("name", "") for e in self.events]

    def storyline_names(self):
        return [s.get("name", "") for s in self.storylines]

    def get_event_by_name(self, name: str):
        return next((e for e in self.events if e.get("name", "").lower() == (name or "").lower()), None)

    def get_event_by_id(self, event_id: str):
        return next((e for e in self.events if e.get("id") == event_id), None)

    def get_match_from_event(self, event_id: str, match_id: str):
        event = self.get_event_by_id(event_id)
        if not event:
            return None
        return next((m for m in event.get("matches", []) if m.get("id") == match_id), None)

    def create_event(self, name: str, date: str, venue: str):
        event = booking.EventCard(name=name, date=date or datetime.utcnow().strftime("%Y-%m-%d"), venue=venue or "")
        booking.upsert_event(event)
        self.reload()
        return event

    def update_event(self, event_id: str, name: str, date: str, venue: str, notes: str = ""):
        updated = booking.update_event(event_id, name=name, date=date, venue=venue, notes=notes)
        self.reload()
        return updated

    def create_storyline(self, name: str, participants):
        storyline = booking.Storyline(name=name, participants=list(participants))
        booking.upsert_storyline(storyline)
        self.reload()
        return storyline

    def add_match_to_event(self, event_id: str, face_side, heel_side, match_type: str, belts=None, storyline_id=None):
        card_match = booking.CardMatch(
            match_type=match_type,
            face_side=list(face_side),
            heel_side=list(heel_side),
            belts=list(belts or []),
            storyline_id=storyline_id,
        )
        booking.add_match_to_event(event_id, card_match)
        self.reload()
        return card_match

    def update_match_in_event(self, event_id: str, match_id: str, face_side, heel_side, match_type: str, belts=None, storyline_id=None):
        updated = booking.CardMatch(
            id=match_id,
            match_type=match_type,
            face_side=list(face_side),
            heel_side=list(heel_side),
            belts=list(belts or []),
            storyline_id=storyline_id,
        )
        booking.update_match_in_event(event_id, updated)
        self.reload()
        return updated

    def remove_match_from_event(self, event_id: str, match_id: str):
        booking.remove_match_from_event(event_id, match_id)
        self.reload()

    def update_timeline_notes(self, index: int, notes: str):
        booking.update_timeline_entry(index, {"notes": notes})
        self.reload()

    def _baseline_wrestler(
        self,
        name,
        persona,
        finisher,
        overall,
        *,
        attributes=None,
        heat_modifier=0,
        overall_modifier=0,
        rivalry_id=None,
        injured=False,
        injury_duration=0,
        titles=None,
        record=None,
        heat=0,
        image="",
    ):
        base_attributes = {
            "size": 0,
            "speed": 0,
            "strength": 0,
            "savvy": 0,
            "cheating": 0,
            "cage": 0,
            "object": 0,
            "ladder": 0,
            "table": 0,
            "tag": 0,
            "technical": 0,
            "brawling": 0,
            "heat": 0,
        }
        merged_attributes = {**base_attributes, **(attributes or {})}
        return {
            "name": name,
            "persona": persona or "Face",
            "finisher": finisher or "",
            "overall": int(overall),
            "attributes": merged_attributes,
            "image": image or "",
            "heat": int(heat),
            "record": record or {"wins": 0, "losses": 0, "draws": 0},
            "injured": bool(injured),
            "injury_duration": int(injury_duration),
            "titles": list(titles or []),
            "rivalry_id": rivalry_id,
            "heat_modifier": int(heat_modifier),
            "overall_modifier": int(overall_modifier),
        }

    def add_wrestler(self, wrestler: dict):
        repository.create_wrestler(wrestler)
        self.reload()

    def update_wrestler(self, existing_name: str, wrestler: dict):
        repository.update_wrestler(existing_name, wrestler)
        self.reload()

    def delete_wrestler(self, name: str):
        repository.delete_wrestler(name)
        self.reload()

    def add_belt(self, name, holder, prestige):
        for belt in self.belts:
            if belt.get("name", "").lower() == name.lower():
                raise ValueError(f"Belt named '{name}' already exists.")
        self.belts.append(
            {
                "name": name,
                "current_holder": holder or "",
                "prestige": int(prestige),
            }
        )
        repository.save_belts(self.belts)

    def update_belt(self, existing_name, holder, prestige):
        for belt in self.belts:
            if belt.get("name") == existing_name:
                belt["current_holder"] = holder or ""
                belt["prestige"] = int(prestige)
                repository.save_belts(self.belts)
                return
        raise ValueError(f"Belt '{existing_name}' not found.")

    def delete_belt(self, name: str):
        repository.delete_belt(name)
        self.reload()


class WrestlerForm(tk.Toplevel):
    ATTRIBUTE_FIELDS = [
        ("strength", "Strength"),
        ("speed", "Speed"),
        ("savvy", "Savvy"),
        ("technical", "Technical"),
        ("cheating", "Cheating"),
        ("size", "Size"),
        ("heat", "Heat"),
        ("cage", "Cage"),
        ("object", "Object"),
        ("brawling", "Brawling"),
        ("ladder", "Ladder"),
        ("table", "Table"),
        ("tag", "Tag"),
    ]

    def __init__(self, master, datastore: DataStore, on_save, existing=None):
        super().__init__(master)
        self.title("Wrestler")
        self.datastore = datastore
        self.on_save = on_save
        self.existing = existing

        record = (existing or {}).get("record", {}) or {}
        attr_defaults = (existing or {}).get("attributes", {}) or {}

        self.name_var = tk.StringVar(value=(existing or {}).get("name", ""))
        self.persona_var = tk.StringVar(value=(existing or {}).get("persona", "Face"))
        self.finisher_var = tk.StringVar(value=(existing or {}).get("finisher", ""))
        self.rivalry_var = tk.StringVar(value=(existing or {}).get("rivalry_id") or "")
        self.titles_var = tk.StringVar(value=", ".join((existing or {}).get("titles", [])))

        self.overall_var = tk.StringVar(value=str((existing or {}).get("overall", 1000)))
        self.overall_modifier_var = tk.StringVar(value=str((existing or {}).get("overall_modifier", 0) or 0))
        self.heat_modifier_var = tk.StringVar(value=str((existing or {}).get("heat_modifier", 0) or 0))
        self.heat_var = tk.StringVar(value=str((existing or {}).get("heat", 0) or 0))

        self.injured_var = tk.BooleanVar(value=bool((existing or {}).get("injured", False)))
        self.injury_duration_var = tk.StringVar(value=str((existing or {}).get("injury_duration", 0)))

        self.wins_var = tk.StringVar(value=str(record.get("wins", 0)))
        self.losses_var = tk.StringVar(value=str(record.get("losses", 0)))
        self.draws_var = tk.StringVar(value=str(record.get("draws", 0)))

        self.attribute_vars = {}
        base_attr = self.datastore._baseline_wrestler("temp", "Face", "", 0)["attributes"]
        for key, _ in self.ATTRIBUTE_FIELDS:
            self.attribute_vars[key] = tk.StringVar(value=str(attr_defaults.get(key, base_attr.get(key, 0))))

        identity_frame = ttk.LabelFrame(self, text="Identity")
        ttk.Label(identity_frame, text="Name").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(identity_frame, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(identity_frame, text="Persona").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        persona_combo = ttk.Combobox(identity_frame, values=["Face", "Heel"], textvariable=self.persona_var, state="readonly")
        persona_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(identity_frame, text="Finisher").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(identity_frame, textvariable=self.finisher_var).grid(row=2, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(identity_frame, text="Rivalry ID").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(identity_frame, textvariable=self.rivalry_var).grid(row=3, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(identity_frame, text="Titles (comma-separated)").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(identity_frame, textvariable=self.titles_var).grid(row=4, column=1, sticky="ew", padx=5, pady=3)

        identity_frame.columnconfigure(1, weight=1)
        identity_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=6)

        rating_frame = ttk.LabelFrame(self, text="Ratings & Status")
        ttk.Label(rating_frame, text="Overall").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(rating_frame, textvariable=self.overall_var).grid(row=0, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(rating_frame, text="Overall Modifier").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(rating_frame, textvariable=self.overall_modifier_var).grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(rating_frame, text="Heat Modifier").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(rating_frame, textvariable=self.heat_modifier_var).grid(row=2, column=1, sticky="ew", padx=5, pady=3)

        ttk.Label(rating_frame, text="Heat").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(rating_frame, textvariable=self.heat_var).grid(row=3, column=1, sticky="ew", padx=5, pady=3)

        ttk.Checkbutton(rating_frame, text="Injured", variable=self.injured_var).grid(row=0, column=2, sticky="w", padx=5, pady=3)
        ttk.Label(rating_frame, text="Injury Duration").grid(row=1, column=2, sticky="e", padx=5, pady=3)
        ttk.Entry(rating_frame, textvariable=self.injury_duration_var, width=8).grid(row=1, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(rating_frame, text="Wins / Losses / Draws").grid(row=2, column=2, sticky="e", padx=5, pady=3)
        record_frame = ttk.Frame(rating_frame)
        ttk.Entry(record_frame, width=6, textvariable=self.wins_var).pack(side=tk.LEFT, padx=2)
        ttk.Entry(record_frame, width=6, textvariable=self.losses_var).pack(side=tk.LEFT, padx=2)
        ttk.Entry(record_frame, width=6, textvariable=self.draws_var).pack(side=tk.LEFT, padx=2)
        record_frame.grid(row=2, column=3, sticky="w", padx=5, pady=3)

        rating_frame.columnconfigure(1, weight=1)
        rating_frame.columnconfigure(3, weight=1)
        rating_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=6)

        attr_frame = ttk.LabelFrame(self, text="Attributes")
        for idx, (key, label) in enumerate(self.ATTRIBUTE_FIELDS):
            row = idx // 2
            col = (idx % 2) * 2
            ttk.Label(attr_frame, text=label).grid(row=row, column=col, sticky="e", padx=5, pady=3)
            ttk.Entry(attr_frame, textvariable=self.attribute_vars[key], width=10).grid(row=row, column=col + 1, sticky="w", padx=5, pady=3)

        attr_frame.columnconfigure(1, weight=1)
        attr_frame.columnconfigure(3, weight=1)
        attr_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=6)

        button_frame = ttk.Frame(self)
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        button_frame.grid(row=3, column=0, pady=8)

        self.columnconfigure(0, weight=1)
        self.resizable(False, False)

    def _save(self):
        name = self.name_var.get().strip()
        persona = self.persona_var.get().strip() or "Face"
        finisher = self.finisher_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required.")
            return
        try:
            overall = int(self.overall_var.get().strip())
            overall_mod = int(self.overall_modifier_var.get().strip() or 0)
            heat_mod = int(self.heat_modifier_var.get().strip() or 0)
            heat = int(self.heat_var.get().strip() or 0)
            injury_duration = int(self.injury_duration_var.get().strip() or 0)
            wins = int(self.wins_var.get().strip() or 0)
            losses = int(self.losses_var.get().strip() or 0)
            draws = int(self.draws_var.get().strip() or 0)
        except ValueError as exc:
            messagebox.showerror("Error", f"Numeric field invalid: {exc}")
            return

        attributes = {}
        try:
            for key, var in self.attribute_vars.items():
                attributes[key] = int(var.get().strip() or 0)
        except ValueError as exc:
            messagebox.showerror("Error", f"Attribute values must be numbers: {exc}")
            return

        titles = [t.strip() for t in self.titles_var.get().split(",") if t.strip()]
        record = {"wins": wins, "losses": losses, "draws": draws}
        payload = self.datastore._baseline_wrestler(
            name,
            persona,
            finisher,
            overall,
            attributes=attributes,
            heat_modifier=heat_mod,
            overall_modifier=overall_mod,
            rivalry_id=self.rivalry_var.get().strip() or None,
            injured=self.injured_var.get(),
            injury_duration=injury_duration,
            titles=titles,
            record=record,
            heat=heat,
            image=(self.existing or {}).get("image", ""),
        )
        if self.existing:
            merged_payload = {**self.existing, **payload}
            try:
                self.datastore.update_wrestler(self.existing.get("name"), merged_payload)
            except ValueError as exc:
                messagebox.showerror("Error", str(exc))
                return
        else:
            try:
                self.datastore.add_wrestler(payload)
            except ValueError as exc:
                messagebox.showerror("Error", str(exc))
                return

        self.on_save()
        self.destroy()


class BeltForm(tk.Toplevel):
    def __init__(self, master, datastore: DataStore, on_save, existing=None):
        super().__init__(master)
        self.title("Belt")
        self.datastore = datastore
        self.on_save = on_save
        self.existing = existing

        name_label = ttk.Label(self, text="Name")
        holder_label = ttk.Label(self, text="Current Holder")
        prestige_label = ttk.Label(self, text="Prestige")

        self.name_var = tk.StringVar(value=existing.get("name") if existing else "")
        self.holder_var = tk.StringVar(value=existing.get("current_holder") if existing else "")
        self.prestige_var = tk.StringVar(value=str(existing.get("prestige", 50)) if existing else "50")

        name_entry = ttk.Entry(self, textvariable=self.name_var, state="disabled" if existing else "normal")
        holder_combo = ttk.Combobox(self, values=self.datastore.wrestler_names(), textvariable=self.holder_var)
        prestige_entry = ttk.Entry(self, textvariable=self.prestige_var)

        save_button = ttk.Button(self, text="Save", command=self._save)
        cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)

        name_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        holder_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        holder_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        prestige_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        prestige_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=5)
        save_button.pack(side=tk.LEFT, padx=5)
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.columnconfigure(1, weight=1)
        self.resizable(False, False)

    def _save(self):
        name = self.name_var.get().strip()
        holder = self.holder_var.get().strip()
        prestige_raw = self.prestige_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required.")
            return
        try:
            prestige = int(prestige_raw)
        except ValueError:
            messagebox.showerror("Error", "Prestige must be a number.")
            return

        try:
            if self.existing:
                self.datastore.update_belt(self.existing.get("name"), holder, prestige)
            else:
                self.datastore.add_belt(name, holder, prestige)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.on_save()
        self.destroy()


class BookingPanel(ttk.Frame):
    def __init__(self, master, datastore: DataStore, on_change=None):
        super().__init__(master, padding=10)
        self.datastore = datastore
        self.on_change = on_change
        self.selected_event_id: str | None = None
        self._editing_match_id: str | None = None
        self._roster_label_to_name: dict[str, str] = {}
        self._build_widgets()
        self.refresh()

    def _build_widgets(self):
        ttk.Label(self, text="Booking & Timeline", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w")

        form = ttk.Frame(self)
        ttk.Label(form, text="Event Name").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(form, text="Venue").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(form, text="Event Notes").grid(row=3, column=0, sticky="ne", padx=5, pady=2)

        self.event_name_var = tk.StringVar()
        self.event_date_var = tk.StringVar(value=datetime.utcnow().strftime("%Y-%m-%d"))
        self.event_venue_var = tk.StringVar()

        ttk.Entry(form, textvariable=self.event_name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Entry(form, textvariable=self.event_date_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Entry(form, textvariable=self.event_venue_var).grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.event_notes_text = tk.Text(form, height=3, width=40)
        self.event_notes_text.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        self.storyline_name_var = tk.StringVar()
        self.storyline_participants_var = tk.StringVar()
        ttk.Label(form, text="Storyline Name").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(form, text="Participants (comma separated)").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        ttk.Entry(form, textvariable=self.storyline_name_var).grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        ttk.Entry(form, textvariable=self.storyline_participants_var).grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        action_buttons = ttk.Frame(form)
        add_event_btn = ttk.Button(action_buttons, text="Save Event", command=self._add_or_update_event)
        new_event_btn = ttk.Button(action_buttons, text="New Event", command=self._new_event)
        add_storyline_btn = ttk.Button(action_buttons, text="Add Storyline", command=self._add_storyline)
        add_event_btn.pack(side=tk.LEFT, padx=4)
        new_event_btn.pack(side=tk.LEFT, padx=4)
        add_storyline_btn.pack(side=tk.LEFT, padx=4)
        action_buttons.grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=4)

        form.columnconfigure(1, weight=1)
        form.grid(row=1, column=0, sticky="ew")

        card = ttk.LabelFrame(self, text="Build Card")
        ttk.Label(card, text="Event").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(card, text="Face Side").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(card, text="Heel Side").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(card, text="Match Type").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(card, text="Storyline").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(card, text="Belts on the line").grid(row=5, column=0, sticky="nw", padx=5, pady=2)

        self.card_event_var = tk.StringVar()
        self.card_match_type_var = tk.StringVar()
        self.card_storyline_var = tk.StringVar()
        self.card_face_select_var = tk.StringVar()
        self.card_heel_select_var = tk.StringVar()

        self.card_event_combo = ttk.Combobox(card, textvariable=self.card_event_var, state="readonly")
        self.card_match_type_combo = ttk.Combobox(card, textvariable=self.card_match_type_var, state="readonly")
        self.card_storyline_combo = ttk.Combobox(card, textvariable=self.card_storyline_var)
        self.card_belts_list = tk.Listbox(card, selectmode=tk.MULTIPLE, height=4, exportselection=False)
        self.card_face_selected_list = tk.Listbox(card, selectmode=tk.EXTENDED, height=4, exportselection=False)
        self.card_heel_selected_list = tk.Listbox(card, selectmode=tk.EXTENDED, height=4, exportselection=False)

        self.card_event_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.card_match_type_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.card_storyline_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.card_belts_list.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        face_side_frame = ttk.Frame(card)
        self.card_face_combo = ttk.Combobox(face_side_frame, textvariable=self.card_face_select_var, state="readonly")
        add_face_btn = ttk.Button(face_side_frame, text="Add Face", command=self._add_face_selection)
        remove_face_btn = ttk.Button(face_side_frame, text="Remove Selected", command=lambda: self._remove_side_entries(self.card_face_selected_list))
        self.card_face_combo.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        add_face_btn.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        remove_face_btn.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.card_face_selected_list.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        face_side_frame.columnconfigure(0, weight=1)
        face_side_frame.columnconfigure(1, weight=1)
        face_side_frame.grid(row=1, column=1, sticky="ew")

        heel_side_frame = ttk.Frame(card)
        self.card_heel_combo = ttk.Combobox(heel_side_frame, textvariable=self.card_heel_select_var, state="readonly")
        add_heel_btn = ttk.Button(heel_side_frame, text="Add Heel", command=self._add_heel_selection)
        remove_heel_btn = ttk.Button(heel_side_frame, text="Remove Selected", command=lambda: self._remove_side_entries(self.card_heel_selected_list))
        self.card_heel_combo.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        add_heel_btn.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        remove_heel_btn.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.card_heel_selected_list.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        heel_side_frame.columnconfigure(0, weight=1)
        heel_side_frame.columnconfigure(1, weight=1)
        heel_side_frame.grid(row=2, column=1, sticky="ew")

        add_match_btn = ttk.Button(card, text="Save Match To Event", command=self._add_match_to_event)
        reset_match_btn = ttk.Button(card, text="Clear Match Form", command=self._reset_match_form)
        add_match_btn.grid(row=6, column=0, sticky="ew", padx=5, pady=4)
        reset_match_btn.grid(row=6, column=1, sticky="ew", padx=5, pady=4)

        card.columnconfigure(1, weight=1)
        card.grid(row=2, column=0, sticky="ew", pady=8)

        events_frame = ttk.LabelFrame(self, text="Events")
        event_columns = ("name", "date", "venue")
        self.event_tree = ttk.Treeview(events_frame, columns=event_columns, show="headings", height=6, selectmode="browse")
        self.event_tree.heading("name", text="Name")
        self.event_tree.heading("date", text="Date")
        self.event_tree.heading("venue", text="Venue")
        for key in event_columns:
            self.event_tree.column(key, width=140 if key == "name" else 110, anchor="w")
        self.event_tree.bind("<<TreeviewSelect>>", self._on_event_select)
        event_scroll = ttk.Scrollbar(events_frame, orient=tk.VERTICAL, command=self.event_tree.yview)
        self.event_tree.configure(yscrollcommand=event_scroll.set)
        self.event_tree.grid(row=0, column=0, sticky="nsew")
        event_scroll.grid(row=0, column=1, sticky="ns")
        events_frame.columnconfigure(0, weight=1)
        events_frame.grid(row=3, column=0, sticky="nsew", pady=6)

        card_frame = ttk.LabelFrame(self, text="Card (selected event)")
        card_columns = ("match", "faces", "heels", "belts", "storyline")
        self.card_tree = ttk.Treeview(card_frame, columns=card_columns, show="headings", height=6)
        headings = {
            "match": "Match Type",
            "faces": "Face Side",
            "heels": "Heel Side",
            "belts": "Belts",
            "storyline": "Storyline",
        }
        for key, title in headings.items():
            self.card_tree.heading(key, text=title)
            self.card_tree.column(key, width=140 if key in {"match", "storyline"} else 160, anchor="w")
        card_scroll = ttk.Scrollbar(card_frame, orient=tk.VERTICAL, command=self.card_tree.yview)
        self.card_tree.configure(yscrollcommand=card_scroll.set)
        self.card_tree.bind("<<TreeviewSelect>>", self._on_card_select)
        self.card_tree.grid(row=0, column=0, sticky="nsew")
        card_scroll.grid(row=0, column=1, sticky="ns")
        remove_match_btn = ttk.Button(card_frame, text="Remove Selected Match", command=self._remove_selected_match)
        remove_match_btn.grid(row=1, column=0, sticky="w", padx=5, pady=4)
        card_frame.columnconfigure(0, weight=1)
        card_frame.grid(row=4, column=0, sticky="nsew")

        timeline_frame = ttk.LabelFrame(self, text="Timeline")
        columns = ("date", "event", "match", "winner", "belts", "storyline", "notes")
        self.timeline_tree = ttk.Treeview(timeline_frame, columns=columns, show="headings", height=8)
        headings = {
            "date": "Date",
            "event": "Event",
            "match": "Match Type",
            "winner": "Winner",
            "belts": "Belts",
            "storyline": "Storyline",
            "notes": "Notes",
        }
        for key, title in headings.items():
            self.timeline_tree.heading(key, text=title)
            self.timeline_tree.column(key, width=110 if key == "date" else 140, anchor="w")

        scroll = ttk.Scrollbar(timeline_frame, orient=tk.VERTICAL, command=self.timeline_tree.yview)
        self.timeline_tree.configure(yscrollcommand=scroll.set)
        self.timeline_tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.timeline_tree.bind("<<TreeviewSelect>>", self._on_timeline_select)

        notes_frame = ttk.Frame(timeline_frame)
        ttk.Label(notes_frame, text="Match Notes").pack(anchor="w")
        self.timeline_notes_text = tk.Text(notes_frame, height=4, width=60)
        self.timeline_notes_text.pack(fill="both", expand=True, pady=2)
        save_note_btn = ttk.Button(notes_frame, text="Save Notes", command=self._save_timeline_note)
        save_note_btn.pack(anchor="w", pady=2)
        notes_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=4)

        timeline_frame.columnconfigure(0, weight=1)
        timeline_frame.rowconfigure(0, weight=1)
        timeline_frame.grid(row=5, column=0, sticky="nsew", pady=8)

        self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)

    def _parse_side(self, raw_value: str):
        return [part.strip() for part in (raw_value or "").split(",") if part.strip()]

    def _label_for_name(self, name: str) -> str:
        for label, actual in self.datastore.wrestler_display_labels():
            if actual == name:
                return label
        return name

    def _add_wrestler_to_side(self, combo: ttk.Combobox, listbox: tk.Listbox):
        label = combo.get()
        if not label:
            return
        name = self._roster_label_to_name.get(label, label)
        existing = [self._roster_label_to_name.get(listbox.get(i), listbox.get(i)) for i in range(listbox.size())]
        if name in existing:
            messagebox.showinfo("Info", f"{name} is already added to this side.")
            return
        listbox.insert(tk.END, label)

    def _add_face_selection(self):
        self._add_wrestler_to_side(self.card_face_combo, self.card_face_selected_list)

    def _add_heel_selection(self):
        self._add_wrestler_to_side(self.card_heel_combo, self.card_heel_selected_list)

    def _remove_side_entries(self, listbox: tk.Listbox):
        selection = listbox.curselection()
        for idx in reversed(selection):
            listbox.delete(idx)

    def _notify_changed(self):
        if callable(self.on_change):
            self.on_change()

    def _new_event(self):
        self.selected_event_id = None
        self._editing_match_id = None
        self.event_name_var.set("")
        self.event_date_var.set(datetime.utcnow().strftime("%Y-%m-%d"))
        self.event_venue_var.set("")
        self._set_event_notes("")
        self.card_event_var.set("")
        self.card_tree.delete(*self.card_tree.get_children())
        self._reset_match_form(clear_event=False)

    def _add_or_update_event(self):
        name = self.event_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Event name is required.")
            return
        date = self.event_date_var.get().strip()
        venue = self.event_venue_var.get().strip()
        notes = self._get_event_notes()
        if self.selected_event_id:
            try:
                self.datastore.update_event(self.selected_event_id, name, date, venue, notes)
            except ValueError as exc:
                messagebox.showerror("Error", str(exc))
                return
        else:
            event = self.datastore.create_event(name, date, venue)
            self.selected_event_id = event.id
            self.card_event_var.set(event.name)
            if notes:
                self.datastore.update_event(self.selected_event_id, name, date, venue, notes)
        self.refresh()
        self._notify_changed()

    def _add_storyline(self):
        name = self.storyline_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Storyline name is required.")
            return
        participants = self._parse_side(self.storyline_participants_var.get())
        if not participants:
            messagebox.showerror("Error", "Provide at least one participant for the storyline.")
            return
        self.datastore.create_storyline(name, participants)
        self.refresh()
        self._notify_changed()

    def _add_match_to_event(self):
        event_name = self.card_event_var.get().strip()
        event = self.datastore.get_event_by_name(event_name)
        if not event:
            messagebox.showerror("Error", "Select a valid event to attach the match.")
            return
        face_side = self._selected_wrestlers(self.card_face_selected_list)
        heel_side = self._selected_wrestlers(self.card_heel_selected_list)
        if not face_side or not heel_side:
            messagebox.showerror("Error", "Select at least one wrestler for each side.")
            return
        match_type = self.card_match_type_var.get().strip()
        if not match_type:
            messagebox.showerror("Error", "Select a match type.")
            return
        storyline_name = self.card_storyline_var.get().strip()
        storyline = next((s for s in self.datastore.storylines if s.get("name") == storyline_name), None)
        storyline_id = storyline.get("id") if storyline else None
        belt_indices = self.card_belts_list.curselection()
        belts = [self.card_belts_list.get(i) for i in belt_indices]

        try:
            if self._editing_match_id:
                self.datastore.update_match_in_event(
                    event.get("id"),
                    self._editing_match_id,
                    face_side,
                    heel_side,
                    match_type,
                    belts=belts,
                    storyline_id=storyline_id,
                )
                message = "Match updated on event card."
            else:
                created = self.datastore.add_match_to_event(
                    event.get("id"), face_side, heel_side, match_type, belts=belts, storyline_id=storyline_id
                )
                self._editing_match_id = created.id
                message = "Match added to event card."
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return

        messagebox.showinfo("Saved", message)
        self.refresh()
        self._notify_changed()

    def _remove_selected_match(self):
        selection = self.card_tree.selection()
        if not selection or not self.selected_event_id:
            messagebox.showinfo("Info", "Select a match to remove.")
            return
        match_id = selection[0]
        try:
            self.datastore.remove_match_from_event(self.selected_event_id, match_id)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._reset_match_form(clear_event=False)
        self.refresh()
        self._notify_changed()

    def _reset_match_form(self, *, clear_event: bool = True):
        if clear_event:
            self.card_event_var.set("")
            self.selected_event_id = None
        self.card_match_type_var.set("")
        self.card_storyline_var.set("")
        self.card_belts_list.selection_clear(0, tk.END)
        self.card_face_selected_list.delete(0, tk.END)
        self.card_heel_selected_list.delete(0, tk.END)
        self._editing_match_id = None

    def _set_event_notes(self, text: str):
        self.event_notes_text.delete("1.0", tk.END)
        self.event_notes_text.insert("1.0", text or "")

    def _get_event_notes(self) -> str:
        return self.event_notes_text.get("1.0", tk.END).strip()

    def _selected_wrestlers(self, listbox: tk.Listbox):
        indices = range(listbox.size())
        names = []
        for idx in indices:
            label = listbox.get(idx)
            name = self._roster_label_to_name.get(label, label)
            names.append(name)
        return names

    def _set_side_entries(self, names: list[str], listbox: tk.Listbox):
        listbox.delete(0, tk.END)
        for name in names:
            label = self._label_for_name(name)
            listbox.insert(tk.END, label)

    def _on_event_select(self, event):
        selection = self.event_tree.selection()
        if not selection:
            return
        event_id = selection[0]
        selected = self.datastore.get_event_by_id(event_id)
        if not selected:
            return
        self.selected_event_id = event_id
        self.event_name_var.set(selected.get("name", ""))
        self.event_date_var.set(selected.get("date", ""))
        self.event_venue_var.set(selected.get("venue", ""))
        self._set_event_notes(selected.get("notes", ""))
        self.card_event_var.set(selected.get("name", ""))
        self._editing_match_id = None
        self._populate_card_matches(selected)

    def _on_card_select(self, event):
        selection = self.card_tree.selection()
        if not selection or not self.selected_event_id:
            return
        match_id = selection[0]
        match = self.datastore.get_match_from_event(self.selected_event_id, match_id)
        if not match:
            return
        self._editing_match_id = match_id
        self.card_match_type_var.set(match.get("match_type", ""))
        self._set_side_entries(match.get("face_side", []), self.card_face_selected_list)
        self._set_side_entries(match.get("heel_side", []), self.card_heel_selected_list)
        belts = match.get("belts", [])
        self.card_belts_list.selection_clear(0, tk.END)
        for idx in range(self.card_belts_list.size()):
            if self.card_belts_list.get(idx) in belts:
                self.card_belts_list.selection_set(idx)
        storyline_id = match.get("storyline_id")
        storyline = next((s for s in self.datastore.storylines if s.get("id") == storyline_id), None)
        if storyline:
            self.card_storyline_var.set(storyline.get("name", ""))
        elif not storyline_id:
            self.card_storyline_var.set("")

    def _populate_timeline(self):
        for row in self.timeline_tree.get_children():
            self.timeline_tree.delete(row)
        events_by_id = {e.get("id"): e.get("name", "") for e in self.datastore.events}
        story_by_id = {s.get("id"): s.get("name", "") for s in self.datastore.storylines}
        for idx, entry in enumerate(self.datastore.timeline):
            event_label = events_by_id.get(entry.get("event_id"), "")
            storyline_label = story_by_id.get(entry.get("storyline_id"), "")
            winner = ", ".join(entry.get("winner", []))
            belts = ", ".join(entry.get("belts", []))
            values = (
                entry.get("occurred_on", ""),
                event_label,
                entry.get("match_type", ""),
                winner,
                belts,
                storyline_label,
                entry.get("notes", ""),
            )
            self.timeline_tree.insert("", tk.END, iid=str(idx), values=values)

    def _on_timeline_select(self, event):
        selection = self.timeline_tree.selection()
        if not selection:
            self.timeline_notes_text.delete("1.0", tk.END)
            return
        idx = int(selection[0])
        entry = self.datastore.timeline[idx]
        notes = entry.get("notes", "")
        self.timeline_notes_text.delete("1.0", tk.END)
        self.timeline_notes_text.insert("1.0", notes)

    def _save_timeline_note(self):
        selection = self.timeline_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Select a timeline entry to add notes.")
            return
        idx = int(selection[0])
        notes = self.timeline_notes_text.get("1.0", tk.END).strip()
        try:
            self.datastore.update_timeline_notes(idx, notes)
        except (IndexError, ValueError) as exc:
            messagebox.showerror("Error", str(exc))
            return
        self.refresh()
        self._notify_changed()

    def refresh(self):
        self.datastore.reload()
        self.card_event_combo.configure(values=self.datastore.event_names())
        if self.datastore.event_names() and not self.card_event_var.get():
            self.card_event_var.set(self.datastore.event_names()[0])
        self.card_match_type_combo.configure(values=self.match_types())
        if self.match_types() and not self.card_match_type_var.get():
            self.card_match_type_var.set(self.match_types()[0])
        self.card_storyline_combo.configure(values=self.datastore.storyline_names())
        self.card_belts_list.delete(0, tk.END)
        for belt in self.datastore.belt_names():
            self.card_belts_list.insert(tk.END, belt)
        roster_labels = [label for label, _ in self.datastore.wrestler_display_labels()]
        self._roster_label_to_name = {label: name for label, name in self.datastore.wrestler_display_labels()}
        self.card_face_combo.configure(values=roster_labels)
        self.card_heel_combo.configure(values=roster_labels)
        if roster_labels and not self.card_face_select_var.get():
            self.card_face_select_var.set(roster_labels[0])
        if roster_labels and not self.card_heel_select_var.get():
            self.card_heel_select_var.set(roster_labels[0])
        self._set_side_entries(self._selected_wrestlers(self.card_face_selected_list), self.card_face_selected_list)
        self._set_side_entries(self._selected_wrestlers(self.card_heel_selected_list), self.card_heel_selected_list)
        self._populate_events()
        self._populate_timeline()
        if self.selected_event_id:
            event = self.datastore.get_event_by_id(self.selected_event_id)
            if event:
                self._populate_card_matches(event)
            else:
                self._new_event()

    def match_types(self):
        game_data = self.datastore.game_data or {}
        types = list((game_data.get("win_charts") or {}).keys())
        tag_types = (game_data.get("tag_win_charts") or {}).keys()
        for match_type in tag_types:
            if match_type not in types:
                types.append(match_type)
        return types

    def _populate_events(self):
        selected_id = self.selected_event_id
        if not selected_id:
            current_sel = self.event_tree.selection()
            selected_id = current_sel[0] if current_sel else None
        for row in self.event_tree.get_children():
            self.event_tree.delete(row)
        for event in self.datastore.events:
            self.event_tree.insert(
                "",
                tk.END,
                iid=event.get("id"),
                values=(event.get("name", ""), event.get("date", ""), event.get("venue", "")),
            )
        if selected_id and self.event_tree.exists(selected_id):
            self.event_tree.selection_set(selected_id)
            self.event_tree.see(selected_id)

    def _populate_card_matches(self, event: dict):
        for row in self.card_tree.get_children():
            self.card_tree.delete(row)
        matches = event.get("matches", [])
        story_by_id = {s.get("id"): s.get("name", "") for s in self.datastore.storylines}
        for match in matches:
            storyline_label = story_by_id.get(match.get("storyline_id"), "")
            belts = ", ".join(match.get("belts", []))
            faces = ", ".join(match.get("face_side", []))
            heels = ", ".join(match.get("heel_side", []))
            match_id = match.get("id", "")
            self.card_tree.insert(
                "",
                tk.END,
                iid=match_id,
                values=(match.get("match_type", ""), faces, heels, belts, storyline_label),
            )

class MatchPanel(ttk.Frame):
    def __init__(self, master, datastore: DataStore, on_timeline_update=None):
        super().__init__(master, padding=10)
        self.datastore = datastore
        self.on_timeline_update = on_timeline_update
        self._init_advanced_rule_vars()
        self._build_widgets()

    def _init_advanced_rule_vars(self):
        defaults = AdvancedRulesConfig()
        self._advanced_defaults = defaults
        self.advanced_enabled_var = tk.BooleanVar(value=False)
        self.enable_injuries_var = tk.BooleanVar(value=defaults.enable_injuries)
        self.enable_titles_var = tk.BooleanVar(value=defaults.enable_titles)
        self.enable_rivalries_var = tk.BooleanVar(value=defaults.enable_rivalries)
        self.enable_heat_var = tk.BooleanVar(value=defaults.enable_heat)
        self.enable_seasons_var = tk.BooleanVar(value=defaults.enable_seasons)
        self.enable_persistent_modifiers_var = tk.BooleanVar(value=defaults.enable_persistent_modifiers)
        self.enable_title_overall_bonus_var = tk.BooleanVar(value=defaults.enable_title_overall_bonus)
        self.heat_change_on_titles_var = tk.BooleanVar(value=defaults.heat_change_on_titles)
        self.clean_win_bonus_var = tk.StringVar(value=str(defaults.clean_win_bonus))
        self.clean_loss_penalty_var = tk.StringVar(value=str(defaults.clean_loss_penalty))
        self.title_overall_bonus_var = tk.StringVar(value=str(defaults.title_overall_bonus))
        self.injury_chance_var = tk.StringVar(value=str(defaults.injury_chance))
        self.base_heat_delta_var = tk.StringVar(value=str(defaults.base_heat_delta))
        self.season_length_var = tk.StringVar(value=str(defaults.season_length))
        self.title_on_the_line_var = tk.StringVar()
        self._advanced_entries: list[ttk.Entry] = []
        self._advanced_checkbuttons: list[ttk.Checkbutton] = []

    def _build_widgets(self):
        ttk.Label(self, text="Match Simulation", font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        ttk.Label(self, text="Event (optional)").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Card Match (optional)").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Storyline (optional)").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Face Wrestler").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Heel Wrestler").grid(row=5, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Match Type").grid(row=6, column=0, sticky="w", pady=2)

        self.event_var = tk.StringVar()
        self.storyline_var = tk.StringVar()
        self.face_var = tk.StringVar()
        self.heel_var = tk.StringVar()
        self.match_type_var = tk.StringVar()
        self.match_card_var = tk.StringVar()
        self._roster_label_to_name: dict[str, str] = {}
        self._match_label_to_id: dict[str, str] = {}
        self._selected_match_id: str | None = None

        self.event_combo = ttk.Combobox(self, values=self.datastore.event_names(), textvariable=self.event_var)
        self.match_card_combo = ttk.Combobox(self, values=[], textvariable=self.match_card_var, state="readonly")
        self.storyline_combo = ttk.Combobox(self, values=self.datastore.storyline_names(), textvariable=self.storyline_var)
        self.face_combo = ttk.Combobox(self, values=[], textvariable=self.face_var, state="readonly")
        self.heel_combo = ttk.Combobox(self, values=[], textvariable=self.heel_var, state="readonly")
        self.match_type_combo = ttk.Combobox(self, values=self._match_types(), textvariable=self.match_type_var, state="readonly")
        self.belt_list = tk.Listbox(self, selectmode=tk.MULTIPLE, height=4, exportselection=False)

        self.event_combo.bind("<<ComboboxSelected>>", self._on_event_change)
        self.match_card_combo.bind("<<ComboboxSelected>>", self._on_match_from_event_selected)

        self.event_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.match_card_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.storyline_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.face_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.heel_combo.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        self.match_type_combo.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Belts on the line (optional)").grid(row=7, column=0, sticky="nw", pady=2)
        self.belt_list.grid(row=7, column=1, sticky="ew", padx=5, pady=2)

        advanced_frame = self._build_advanced_rules_frame()
        advanced_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=6)

        simulate_button = ttk.Button(self, text="Simulate", command=self._simulate)
        simulate_button.grid(row=9, column=0, columnspan=2, pady=8)

        log_frame = ttk.LabelFrame(self, text="Result Log")
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        log_frame.grid(row=10, column=0, columnspan=2, sticky="nsew", pady=5)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll.grid(row=0, column=1, sticky="ns")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(10, weight=1)

    def _build_advanced_rules_frame(self):
        frame = ttk.LabelFrame(self, text="Advanced Rules")
        ttk.Checkbutton(frame, text="Enable advanced rules", variable=self.advanced_enabled_var, command=self._toggle_advanced_controls).grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )

        toggles = [
            ("Injuries", self.enable_injuries_var),
            ("Titles", self.enable_titles_var),
            ("Rivalries", self.enable_rivalries_var),
            ("Heat", self.enable_heat_var),
            ("Seasons", self.enable_seasons_var),
            ("Persistent Modifiers", self.enable_persistent_modifiers_var),
            ("Title Overall Bonus", self.enable_title_overall_bonus_var),
            ("Heat on Title Changes", self.heat_change_on_titles_var),
        ]
        toggle_frame = ttk.Frame(frame)
        for idx, (label, var) in enumerate(toggles):
            chk = ttk.Checkbutton(toggle_frame, text=label, variable=var)
            chk.grid(row=idx // 3, column=idx % 3, sticky="w", padx=4, pady=2)
            self._advanced_checkbuttons.append(chk)
        toggle_frame.grid(row=1, column=0, columnspan=6, sticky="w")

        numeric_fields = [
            ("Clean Win Bonus", self.clean_win_bonus_var),
            ("Clean Loss Penalty", self.clean_loss_penalty_var),
            ("Title Overall Bonus", self.title_overall_bonus_var),
            ("Injury Chance", self.injury_chance_var),
            ("Base Heat Delta", self.base_heat_delta_var),
            ("Season Length", self.season_length_var),
        ]
        for idx, (label, var) in enumerate(numeric_fields):
            row = idx // 3
            col = (idx % 3) * 2
            ttk.Label(frame, text=label).grid(row=row + 2, column=col, sticky="e", padx=4, pady=2)
            entry = ttk.Entry(frame, textvariable=var, width=10)
            entry.grid(row=row + 2, column=col + 1, sticky="w", padx=4, pady=2)
            self._advanced_entries.append(entry)

        last_row = 2 + (len(numeric_fields) - 1) // 3
        ttk.Label(frame, text="Title on the Line (optional)").grid(row=last_row + 1, column=0, sticky="e", padx=4, pady=2)
        title_entry = ttk.Entry(frame, textvariable=self.title_on_the_line_var)
        title_entry.grid(row=last_row + 1, column=1, sticky="w", padx=4, pady=2, columnspan=3)
        self._advanced_entries.append(title_entry)

        for col in range(6):
            frame.columnconfigure(col, weight=1)
        self._toggle_advanced_controls()
        return frame

    def _toggle_advanced_controls(self):
        state = "normal" if self.advanced_enabled_var.get() else "disabled"
        for widget in self._advanced_entries:
            widget.configure(state=state)
        for widget in self._advanced_checkbuttons:
            if state == "disabled":
                widget.state(["disabled"])
            else:
                widget.state(["!disabled"])

    def _collect_advanced_config(self):
        if not self.advanced_enabled_var.get():
            return None
        try:
            config = {
                "enabled": True,
                "enable_injuries": self.enable_injuries_var.get(),
                "enable_titles": self.enable_titles_var.get(),
                "enable_rivalries": self.enable_rivalries_var.get(),
                "enable_heat": self.enable_heat_var.get(),
                "enable_seasons": self.enable_seasons_var.get(),
                "enable_persistent_modifiers": self.enable_persistent_modifiers_var.get(),
                "enable_title_overall_bonus": self.enable_title_overall_bonus_var.get(),
                "heat_change_on_titles": self.heat_change_on_titles_var.get(),
                "clean_win_bonus": int(self.clean_win_bonus_var.get() or 0),
                "clean_loss_penalty": int(self.clean_loss_penalty_var.get() or 0),
                "title_overall_bonus": int(self.title_overall_bonus_var.get() or 0),
                "injury_chance": float(self.injury_chance_var.get() or self._advanced_defaults.injury_chance),
                "base_heat_delta": int(self.base_heat_delta_var.get() or self._advanced_defaults.base_heat_delta),
                "season_length": int(self.season_length_var.get() or self._advanced_defaults.season_length),
            }
        except ValueError as exc:
            raise ValueError(f"Invalid advanced rule value: {exc}")

        title_on_the_line = self.title_on_the_line_var.get().strip()
        if title_on_the_line:
            config["title_on_the_line"] = title_on_the_line
        return config

    def _match_types(self):
        game_data = self.datastore.game_data or {}
        types = list((game_data.get("win_charts") or {}).keys())
        tag_types = (game_data.get("tag_win_charts") or {}).keys()
        for match_type in tag_types:
            if match_type not in types:
                types.append(match_type)
        return types

    def _roster_labels(self):
        labels = self.datastore.wrestler_display_labels()
        self._roster_label_to_name = {label: name for label, name in labels}
        return [label for label, _ in labels]

    def _name_from_label(self, label: str) -> str:
        return self._roster_label_to_name.get(label, label)

    def _label_for_name(self, name: str) -> str:
        for label, actual in self.datastore.wrestler_display_labels():
            if actual == name:
                return label
        return name

    def _populate_match_choices(self, event_name: str):
        matches = []
        self._match_label_to_id = {}
        self._selected_match_id = None
        event = self.datastore.get_event_by_name(event_name) if event_name else None
        if event:
            for idx, match in enumerate(event.get("matches", []), start=1):
                faces = ", ".join(match.get("face_side", []))
                heels = ", ".join(match.get("heel_side", []))
                label = f"{idx}. {match.get('match_type', '')}: {faces} vs {heels}"
                self._match_label_to_id[label] = match.get("id")
                matches.append(label)
        self.match_card_combo.configure(values=matches)
        if matches:
            if self.match_card_var.get() not in matches:
                self.match_card_var.set(matches[0])
            self._on_match_from_event_selected()
        else:
            self.match_card_var.set("")
            self._selected_match_id = None

    def _set_belt_selection(self, belts: list[str]):
        self.belt_list.selection_clear(0, tk.END)
        for idx in range(self.belt_list.size()):
            if self.belt_list.get(idx) in belts:
                self.belt_list.selection_set(idx)

    def _apply_match_to_form(self, match: dict):
        face_side = match.get("face_side", [])
        heel_side = match.get("heel_side", [])
        if face_side:
            self.face_var.set(self._label_for_name(face_side[0]))
        if heel_side:
            self.heel_var.set(self._label_for_name(heel_side[0]))
        if match.get("match_type"):
            self.match_type_var.set(match.get("match_type"))
        self._set_belt_selection(match.get("belts", []))
        storyline_id = match.get("storyline_id")
        storyline = next((s for s in self.datastore.storylines if s.get("id") == storyline_id), None)
        if storyline:
            self.storyline_var.set(storyline.get("name", ""))

    def _on_event_change(self, event=None):
        self._populate_match_choices(self.event_var.get())

    def _on_match_from_event_selected(self, event=None):
        label = self.match_card_var.get()
        self._selected_match_id = self._match_label_to_id.get(label)
        if not self._selected_match_id:
            return
        event = self.datastore.get_event_by_name(self.event_var.get().strip()) if self.event_var.get() else None
        if not event:
            return
        match = self.datastore.get_match_from_event(event.get("id"), self._selected_match_id)
        if match:
            self._apply_match_to_form(match)

    def refresh(self):
        roster_labels = self._roster_labels()
        self.face_combo.configure(values=roster_labels)
        self.heel_combo.configure(values=roster_labels)
        match_types = self._match_types()
        self.match_type_combo.configure(values=match_types)
        self.event_combo.configure(values=self.datastore.event_names())
        self.storyline_combo.configure(values=self.datastore.storyline_names())
        self.belt_list.delete(0, tk.END)
        for belt in self.datastore.belt_names():
            self.belt_list.insert(tk.END, belt)
        if roster_labels and not self.face_var.get():
            self.face_var.set(roster_labels[0])
        if len(roster_labels) > 1 and not self.heel_var.get():
            self.heel_var.set(roster_labels[1])
        elif roster_labels and not self.heel_var.get():
            self.heel_var.set(roster_labels[0])
        if match_types and not self.match_type_var.get():
            self.match_type_var.set(match_types[0])
        if self.datastore.event_names() and not self.event_var.get():
            self.event_var.set(self.datastore.event_names()[0])
        if self.datastore.storyline_names() and not self.storyline_var.get():
            self.storyline_var.set(self.datastore.storyline_names()[0])
        self._populate_match_choices(self.event_var.get())

    def _simulate(self):
        face_label = self.face_var.get()
        heel_label = self.heel_var.get()
        face_name = self._name_from_label(face_label)
        heel_name = self._name_from_label(heel_label)
        match_type = self.match_type_var.get()
        if not face_name or not heel_name:
            messagebox.showerror("Error", "Select both wrestlers.")
            return
        if face_name == heel_name:
            messagebox.showerror("Error", "Choose different wrestlers for each side.")
            return
        if not match_type:
            messagebox.showerror("Error", "Select a match type.")
            return
        belt_indices = self.belt_list.curselection()
        belts = [self.belt_list.get(i) for i in belt_indices]

        face = next((w for w in self.datastore.wrestlers if w.get("name") == face_name), None)
        heel = next((w for w in self.datastore.wrestlers if w.get("name") == heel_name), None)
        if not face or not heel:
            messagebox.showerror("Error", "Could not load wrestler data.")
            return

        assigned_roles = {"Face": [face_name], "Heel": [heel_name]}
        event_name = self.event_var.get().strip()
        storyline_name = self.storyline_var.get().strip()
        storyline_id = None
        if storyline_name:
            storyline = next((s for s in self.datastore.storylines if s.get("name") == storyline_name), None)
            if not storyline:
                storyline = self.datastore.create_storyline(storyline_name, assigned_roles["Face"] + assigned_roles["Heel"])
            storyline_id = storyline.get("id")
        event = self.datastore.get_event_by_name(event_name) if event_name else None
        if event_name and not event:
            event = self.datastore.create_event(event_name, datetime.utcnow().strftime("%Y-%m-%d"), "")
        match_card_id = None
        event_id = event.get("id") if event else None
        if event:
            try:
                if self._selected_match_id:
                    self.datastore.update_match_in_event(
                        event_id, self._selected_match_id, assigned_roles["Face"], assigned_roles["Heel"], match_type, belts=belts, storyline_id=storyline_id
                    )
                    match_card_id = self._selected_match_id
                else:
                    card_match = self.datastore.add_match_to_event(
                        event_id, assigned_roles["Face"], assigned_roles["Heel"], match_type, belts=belts, storyline_id=storyline_id
                    )
                    match_card_id = card_match.id
                    self._selected_match_id = match_card_id
            except ValueError as exc:
                messagebox.showerror("Error", str(exc))
                return
        booking_context = booking.MatchBookingContext(
            event_id=event_id, match_id=match_card_id, storyline_id=storyline_id, belts=belts
        )
        try:
            advanced_config = self._collect_advanced_config()
        except ValueError as exc:
            messagebox.showerror("Advanced Rules", str(exc))
            return
        try:
            match = create_match(
                face,
                heel,
                match_type,
                self.datastore.game_data,
                assigned_roles,
                booking_context=booking_context,
                advanced_rules_config=advanced_config,
            )
            log_output = match.simulate()
        except Exception as exc:
            messagebox.showerror("Simulation error", str(exc))
            return
        self.datastore.reload()
        self.refresh()
        if callable(self.on_timeline_update):
            self.on_timeline_update()

        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, log_output)
        self.log_text.configure(state=tk.DISABLED)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ultra Quick Wrestling - Manager")
        self.geometry("800x700")
        self.datastore = DataStore()
        self._build_layout()

    def _build_layout(self):
        notebook = ttk.Notebook(self)
        wrestler_tab = ttk.Frame(notebook, padding=10)
        belt_tab = ttk.Frame(notebook, padding=10)
        match_tab = ttk.Frame(notebook, padding=10)
        booking_tab = ttk.Frame(notebook, padding=10)

        notebook.add(wrestler_tab, text="Wrestlers")
        notebook.add(belt_tab, text="Belts")
        notebook.add(match_tab, text="Match Simulator")
        notebook.add(booking_tab, text="Booking")
        notebook.pack(fill=tk.BOTH, expand=True)

        self._build_wrestler_tab(wrestler_tab)
        self._build_belt_tab(belt_tab)
        self.match_panel = MatchPanel(match_tab, self.datastore, on_timeline_update=self._refresh_booking)
        self.match_panel.pack(fill=tk.BOTH, expand=True)
        self.booking_panel = BookingPanel(booking_tab, self.datastore, on_change=self._refresh_all)
        self.booking_panel.pack(fill=tk.BOTH, expand=True)

    def _build_wrestler_tab(self, parent):
        header = ttk.Label(parent, text="Wrestlers", font=("TkDefaultFont", 12, "bold"))
        header.pack(anchor="w")

        columns = ("name", "persona", "finisher", "overall")
        self.wrestler_tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse", height=12)
        self.wrestler_tree.heading("name", text="Name")
        self.wrestler_tree.heading("persona", text="Persona")
        self.wrestler_tree.heading("finisher", text="Finisher")
        self.wrestler_tree.heading("overall", text="Overall")
        self.wrestler_tree.column("name", width=160)
        self.wrestler_tree.column("persona", width=100)
        self.wrestler_tree.column("finisher", width=200)
        self.wrestler_tree.column("overall", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.wrestler_tree.yview)
        self.wrestler_tree.configure(yscrollcommand=scrollbar.set)

        self._populate_wrestler_tree()

        controls = ttk.Frame(parent)
        add_btn = ttk.Button(controls, text="Add Wrestler", command=self._open_add_wrestler)
        edit_btn = ttk.Button(controls, text="Edit Selected", command=self._open_edit_wrestler)
        delete_btn = ttk.Button(controls, text="Delete Selected", command=self._delete_wrestler)
        refresh_btn = ttk.Button(controls, text="Refresh", command=self._refresh_all)

        add_btn.pack(side=tk.LEFT, padx=5)
        edit_btn.pack(side=tk.LEFT, padx=5)
        delete_btn.pack(side=tk.LEFT, padx=5)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        self.wrestler_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        controls.pack(anchor="w", pady=5)

    def _build_belt_tab(self, parent):
        header = ttk.Label(parent, text="Belts", font=("TkDefaultFont", 12, "bold"))
        header.pack(anchor="w")

        columns = ("name", "holder", "prestige")
        self.belt_tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse", height=10)
        self.belt_tree.heading("name", text="Name")
        self.belt_tree.heading("holder", text="Current Holder")
        self.belt_tree.heading("prestige", text="Prestige")
        self.belt_tree.column("name", width=180)
        self.belt_tree.column("holder", width=200)
        self.belt_tree.column("prestige", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.belt_tree.yview)
        self.belt_tree.configure(yscrollcommand=scrollbar.set)

        self._populate_belt_tree()

        controls = ttk.Frame(parent)
        add_btn = ttk.Button(controls, text="Add Belt", command=self._open_add_belt)
        edit_btn = ttk.Button(controls, text="Edit Selected", command=self._open_edit_belt)
        delete_btn = ttk.Button(controls, text="Delete Selected", command=self._delete_belt)
        refresh_btn = ttk.Button(controls, text="Refresh", command=self._refresh_all)

        add_btn.pack(side=tk.LEFT, padx=5)
        edit_btn.pack(side=tk.LEFT, padx=5)
        delete_btn.pack(side=tk.LEFT, padx=5)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        self.belt_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        controls.pack(anchor="w", pady=5)

    def _populate_wrestler_tree(self):
        for row in self.wrestler_tree.get_children():
            self.wrestler_tree.delete(row)
        for wrestler in self.datastore.wrestlers:
            name = wrestler.get("name")
            self.wrestler_tree.insert("", tk.END, iid=name, values=(name, wrestler.get("persona"), wrestler.get("finisher"), wrestler.get("overall")))

    def _populate_belt_tree(self):
        for row in self.belt_tree.get_children():
            self.belt_tree.delete(row)
        for belt in self.datastore.belts:
            name = belt.get("name")
            self.belt_tree.insert("", tk.END, iid=name, values=(name, belt.get("current_holder"), belt.get("prestige")))

    def _open_add_wrestler(self):
        WrestlerForm(self, self.datastore, on_save=self._refresh_all)

    def _open_edit_wrestler(self):
        selection = self.wrestler_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Select a wrestler to edit.")
            return
        name = selection[0]
        wrestler = next((w for w in self.datastore.wrestlers if w.get("name") == name), None)
        if wrestler:
            WrestlerForm(self, self.datastore, on_save=self._refresh_all, existing=wrestler)

    def _delete_wrestler(self):
        selection = self.wrestler_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Select a wrestler to delete.")
            return
        name = selection[0]
        if not messagebox.askyesno("Confirm", f"Delete wrestler '{name}'?"):
            return
        try:
            self.datastore.delete_wrestler(name)
            self._refresh_all()
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def _open_add_belt(self):
        BeltForm(self, self.datastore, on_save=self._refresh_all)

    def _open_edit_belt(self):
        selection = self.belt_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Select a belt to edit.")
            return
        name = selection[0]
        belt = next((b for b in self.datastore.belts if b.get("name") == name), None)
        if belt:
            BeltForm(self, self.datastore, on_save=self._refresh_all, existing=belt)

    def _delete_belt(self):
        selection = self.belt_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Select a belt to delete.")
            return
        name = selection[0]
        if not messagebox.askyesno("Confirm", f"Delete belt '{name}'?"):
            return
        try:
            self.datastore.delete_belt(name)
            self._refresh_all()
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def _refresh_all(self):
        self.datastore.reload()
        self._populate_wrestler_tree()
        self._populate_belt_tree()
        self.match_panel.refresh()
        self._refresh_booking()

    def _refresh_booking(self):
        if hasattr(self, "booking_panel"):
            self.booking_panel.refresh()


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()

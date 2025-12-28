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
        return [w.get("name", "") for w in self.wrestlers]

    def belt_names(self):
        return [b.get("name", "") for b in self.belts]

    def event_names(self):
        return [e.get("name", "") for e in self.events]

    def storyline_names(self):
        return [s.get("name", "") for s in self.storylines]

    def get_event_by_name(self, name: str):
        return next((e for e in self.events if e.get("name", "").lower() == (name or "").lower()), None)

    def create_event(self, name: str, date: str, venue: str):
        event = booking.EventCard(name=name, date=date or datetime.utcnow().strftime("%Y-%m-%d"), venue=venue or "")
        booking.upsert_event(event)
        self.reload()
        return event

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

    def _baseline_wrestler(self, name, persona, finisher, overall):
        return {
            "name": name,
            "persona": persona or "Face",
            "finisher": finisher or "",
            "overall": int(overall),
            "attributes": {
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
            },
            "image": "",
            "heat": 0,
            "record": {"wins": 0, "losses": 0, "draws": 0},
            "injured": False,
            "injury_duration": 0,
            "titles": [],
            "rivalry_id": None,
            "heat_modifier": 0,
            "overall_modifier": 0,
        }

    def add_wrestler(self, name, persona, finisher, overall):
        new_wrestler = self._baseline_wrestler(name, persona, finisher, overall)
        repository.create_wrestler(new_wrestler)
        self.reload()

    def update_wrestler(self, existing_name, persona, finisher, overall):
        updates = {
            "persona": persona or None,
            "finisher": finisher if finisher is not None else None,
            "overall": int(overall),
        }
        cleaned_updates = {k: v for k, v in updates.items() if v is not None}
        repository.update_wrestler(existing_name, cleaned_updates)
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


class WrestlerForm(tk.Toplevel):
    def __init__(self, master, datastore: DataStore, on_save, existing=None):
        super().__init__(master)
        self.title("Wrestler")
        self.datastore = datastore
        self.on_save = on_save
        self.existing = existing

        name_label = ttk.Label(self, text="Name")
        persona_label = ttk.Label(self, text="Persona")
        finisher_label = ttk.Label(self, text="Finisher")
        overall_label = ttk.Label(self, text="Overall")

        self.name_var = tk.StringVar(value=existing.get("name") if existing else "")
        self.persona_var = tk.StringVar(value=existing.get("persona") if existing else "Face")
        self.finisher_var = tk.StringVar(value=existing.get("finisher") if existing else "")
        self.overall_var = tk.StringVar(value=str(existing.get("overall", 1000)) if existing else "1000")

        name_entry = ttk.Entry(self, textvariable=self.name_var, state="disabled" if existing else "normal")
        persona_combo = ttk.Combobox(self, values=["Face", "Heel"], textvariable=self.persona_var, state="readonly")
        finisher_entry = ttk.Entry(self, textvariable=self.finisher_var)
        overall_entry = ttk.Entry(self, textvariable=self.overall_var)

        save_button = ttk.Button(self, text="Save", command=self._save)
        cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)

        name_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        persona_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        persona_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        finisher_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        finisher_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        overall_label.grid(row=3, column=0, sticky="e", padx=5, pady=5)
        overall_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=5)
        save_button.pack(side=tk.LEFT, padx=5)
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.columnconfigure(1, weight=1)
        self.resizable(False, False)

    def _save(self):
        name = self.name_var.get().strip()
        persona = self.persona_var.get().strip() or "Face"
        finisher = self.finisher_var.get().strip()
        overall_raw = self.overall_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required.")
            return
        try:
            overall = int(overall_raw)
        except ValueError:
            messagebox.showerror("Error", "Overall must be a number.")
            return

        try:
            if self.existing:
                self.datastore.update_wrestler(self.existing.get("name"), persona, finisher, overall)
            else:
                self.datastore.add_wrestler(name, persona, finisher, overall)
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
    def __init__(self, master, datastore: DataStore):
        super().__init__(master, padding=10)
        self.datastore = datastore
        self._build_widgets()
        self.refresh()

    def _build_widgets(self):
        ttk.Label(self, text="Booking & Timeline", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w")

        form = ttk.Frame(self)
        ttk.Label(form, text="Event Name").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(form, text="Venue").grid(row=2, column=0, sticky="e", padx=5, pady=2)

        self.event_name_var = tk.StringVar()
        self.event_date_var = tk.StringVar(value=datetime.utcnow().strftime("%Y-%m-%d"))
        self.event_venue_var = tk.StringVar()

        ttk.Entry(form, textvariable=self.event_name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Entry(form, textvariable=self.event_date_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Entry(form, textvariable=self.event_venue_var).grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        self.storyline_name_var = tk.StringVar()
        self.storyline_participants_var = tk.StringVar()
        ttk.Label(form, text="Storyline Name").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(form, text="Participants (comma separated)").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        ttk.Entry(form, textvariable=self.storyline_name_var).grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Entry(form, textvariable=self.storyline_participants_var).grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        add_event_btn = ttk.Button(form, text="Add Event", command=self._add_event)
        add_event_btn.grid(row=5, column=0, sticky="ew", padx=5, pady=4)

        add_storyline_btn = ttk.Button(form, text="Add Storyline", command=self._add_storyline)
        add_storyline_btn.grid(row=5, column=1, sticky="ew", padx=5, pady=4)

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
        self.card_face_var = tk.StringVar()
        self.card_heel_var = tk.StringVar()
        self.card_match_type_var = tk.StringVar()
        self.card_storyline_var = tk.StringVar()

        self.card_event_combo = ttk.Combobox(card, textvariable=self.card_event_var)
        self.card_face_entry = ttk.Entry(card, textvariable=self.card_face_var)
        self.card_heel_entry = ttk.Entry(card, textvariable=self.card_heel_var)
        self.card_match_type_combo = ttk.Combobox(card, textvariable=self.card_match_type_var)
        self.card_storyline_combo = ttk.Combobox(card, textvariable=self.card_storyline_var)
        self.card_belts_list = tk.Listbox(card, selectmode=tk.MULTIPLE, height=4, exportselection=False)

        self.card_event_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.card_face_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.card_heel_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.card_match_type_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.card_storyline_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.card_belts_list.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        add_match_btn = ttk.Button(card, text="Add Match To Event", command=self._add_match_to_event)
        add_match_btn.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=4)

        card.columnconfigure(1, weight=1)
        card.grid(row=2, column=0, sticky="ew", pady=8)

        timeline_frame = ttk.LabelFrame(self, text="Timeline")
        columns = ("date", "event", "match", "winner", "belts", "storyline")
        self.timeline_tree = ttk.Treeview(timeline_frame, columns=columns, show="headings", height=10)
        headings = {
            "date": "Date",
            "event": "Event",
            "match": "Match Type",
            "winner": "Winner",
            "belts": "Belts",
            "storyline": "Storyline",
        }
        for key, title in headings.items():
            self.timeline_tree.heading(key, text=title)
            self.timeline_tree.column(key, width=110 if key == "date" else 140, anchor="w")

        scroll = ttk.Scrollbar(timeline_frame, orient=tk.VERTICAL, command=self.timeline_tree.yview)
        self.timeline_tree.configure(yscrollcommand=scroll.set)
        self.timeline_tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        timeline_frame.columnconfigure(0, weight=1)
        timeline_frame.rowconfigure(0, weight=1)
        timeline_frame.grid(row=3, column=0, sticky="nsew", pady=8)

        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)

    def _parse_side(self, raw_value: str):
        return [part.strip() for part in (raw_value or "").split(",") if part.strip()]

    def _add_event(self):
        name = self.event_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Event name is required.")
            return
        self.datastore.create_event(name, self.event_date_var.get().strip(), self.event_venue_var.get().strip())
        self.refresh()

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

    def _add_match_to_event(self):
        event_name = self.card_event_var.get().strip()
        event = self.datastore.get_event_by_name(event_name)
        if not event:
            messagebox.showerror("Error", "Select a valid event to attach the match.")
            return
        face_side = self._parse_side(self.card_face_var.get())
        heel_side = self._parse_side(self.card_heel_var.get())
        if not face_side or not heel_side:
            messagebox.showerror("Error", "Provide comma-separated names for both sides.")
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
            self.datastore.add_match_to_event(event.get("id"), face_side, heel_side, match_type, belts=belts, storyline_id=storyline_id)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return

        messagebox.showinfo("Added", "Match added to event card.")
        self.refresh()

    def _populate_timeline(self):
        for row in self.timeline_tree.get_children():
            self.timeline_tree.delete(row)
        events_by_id = {e.get("id"): e.get("name", "") for e in self.datastore.events}
        story_by_id = {s.get("id"): s.get("name", "") for s in self.datastore.storylines}
        for entry in self.datastore.timeline:
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
            )
            self.timeline_tree.insert("", tk.END, values=values)

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
        self._populate_timeline()

    def match_types(self):
        game_data = self.datastore.game_data or {}
        types = list((game_data.get("win_charts") or {}).keys())
        tag_types = (game_data.get("tag_win_charts") or {}).keys()
        for match_type in tag_types:
            if match_type not in types:
                types.append(match_type)
        return types

class MatchPanel(ttk.Frame):
    def __init__(self, master, datastore: DataStore, on_timeline_update=None):
        super().__init__(master, padding=10)
        self.datastore = datastore
        self.on_timeline_update = on_timeline_update
        self._build_widgets()

    def _build_widgets(self):
        ttk.Label(self, text="Match Simulation", font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        ttk.Label(self, text="Event (optional)").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Storyline (optional)").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Face Wrestler").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Heel Wrestler").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Match Type").grid(row=5, column=0, sticky="w", pady=2)

        wrestler_names = self.datastore.wrestler_names()
        self.event_var = tk.StringVar()
        self.storyline_var = tk.StringVar()
        self.face_var = tk.StringVar(value=wrestler_names[0] if wrestler_names else "")
        self.heel_var = tk.StringVar(value=wrestler_names[1] if len(wrestler_names) > 1 else "")
        self.match_type_var = tk.StringVar()

        self.event_combo = ttk.Combobox(self, values=self.datastore.event_names(), textvariable=self.event_var)
        self.storyline_combo = ttk.Combobox(self, values=self.datastore.storyline_names(), textvariable=self.storyline_var)
        self.face_combo = ttk.Combobox(self, values=wrestler_names, textvariable=self.face_var)
        self.heel_combo = ttk.Combobox(self, values=wrestler_names, textvariable=self.heel_var)
        self.match_type_combo = ttk.Combobox(self, values=self._match_types(), textvariable=self.match_type_var, state="readonly")
        self.belt_list = tk.Listbox(self, selectmode=tk.MULTIPLE, height=4, exportselection=False)

        if self._match_types():
            self.match_type_var.set(self._match_types()[0])

        simulate_button = ttk.Button(self, text="Simulate", command=self._simulate)

        log_frame = ttk.LabelFrame(self, text="Result Log")
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.event_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.storyline_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.face_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.heel_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.match_type_combo.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Belts on the line (optional)").grid(row=6, column=0, sticky="nw", pady=2)
        self.belt_list.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        simulate_button.grid(row=7, column=0, columnspan=2, pady=8)

        log_frame.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=5)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll.grid(row=0, column=1, sticky="ns")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(8, weight=1)

    def _match_types(self):
        game_data = self.datastore.game_data or {}
        types = list((game_data.get("win_charts") or {}).keys())
        tag_types = (game_data.get("tag_win_charts") or {}).keys()
        for match_type in tag_types:
            if match_type not in types:
                types.append(match_type)
        return types

    def refresh(self):
        wrestler_names = self.datastore.wrestler_names()
        self.face_combo.configure(values=wrestler_names)
        self.heel_combo.configure(values=wrestler_names)
        match_types = self._match_types()
        self.match_type_combo.configure(values=match_types)
        self.event_combo.configure(values=self.datastore.event_names())
        self.storyline_combo.configure(values=self.datastore.storyline_names())
        self.belt_list.delete(0, tk.END)
        for belt in self.datastore.belt_names():
            self.belt_list.insert(tk.END, belt)
        if wrestler_names and not self.face_var.get():
            self.face_var.set(wrestler_names[0])
        if len(wrestler_names) > 1 and not self.heel_var.get():
            self.heel_var.set(wrestler_names[1])
        if match_types and not self.match_type_var.get():
            self.match_type_var.set(match_types[0])
        if self.datastore.event_names() and not self.event_var.get():
            self.event_var.set(self.datastore.event_names()[0])
        if self.datastore.storyline_names() and not self.storyline_var.get():
            self.storyline_var.set(self.datastore.storyline_names()[0])

    def _simulate(self):
        face_name = self.face_var.get()
        heel_name = self.heel_var.get()
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
        event_id = None
        if event:
            card_match = self.datastore.add_match_to_event(
                event.get("id"), assigned_roles["Face"], assigned_roles["Heel"], match_type, belts=belts, storyline_id=storyline_id
            )
            event_id = event.get("id")
            match_card_id = card_match.id
        booking_context = booking.MatchBookingContext(
            event_id=event_id, match_id=match_card_id, storyline_id=storyline_id, belts=belts
        )
        try:
            match = create_match(face, heel, match_type, self.datastore.game_data, assigned_roles, booking_context=booking_context)
            log_output = match.simulate()
        except Exception as exc:
            messagebox.showerror("Simulation error", str(exc))
            return
        self.datastore.reload()
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
        self.booking_panel = BookingPanel(booking_tab, self.datastore)
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
        refresh_btn = ttk.Button(controls, text="Refresh", command=self._refresh_all)

        add_btn.pack(side=tk.LEFT, padx=5)
        edit_btn.pack(side=tk.LEFT, padx=5)
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
        refresh_btn = ttk.Button(controls, text="Refresh", command=self._refresh_all)

        add_btn.pack(side=tk.LEFT, padx=5)
        edit_btn.pack(side=tk.LEFT, padx=5)
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

import tkinter as tk
from tkinter import messagebox, ttk

from engine import data_loader
from engine.match import create_match


class DataStore:
    def __init__(self):
        self.reload()

    def reload(self):
        self.wrestlers = data_loader.load_wrestlers()
        self.belts = data_loader.load_belts()
        self.game_data = data_loader.load_game_data()

    def wrestler_names(self):
        return [w.get("name", "") for w in self.wrestlers]

    def belt_names(self):
        return [b.get("name", "") for b in self.belts]

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
        for wrestler in self.wrestlers:
            if wrestler.get("name", "").lower() == name.lower():
                raise ValueError(f"Wrestler named '{name}' already exists.")
        new_wrestler = self._baseline_wrestler(name, persona, finisher, overall)
        self.wrestlers.append(new_wrestler)
        data_loader.save_wrestlers(self.wrestlers)

    def update_wrestler(self, existing_name, persona, finisher, overall):
        for wrestler in self.wrestlers:
            if wrestler.get("name") == existing_name:
                wrestler["persona"] = persona or wrestler.get("persona")
                wrestler["finisher"] = finisher if finisher is not None else wrestler.get("finisher", "")
                wrestler["overall"] = int(overall)
                data_loader.save_wrestlers(self.wrestlers)
                return
        raise ValueError(f"Wrestler '{existing_name}' not found.")

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
        data_loader.save_belts(self.belts)

    def update_belt(self, existing_name, holder, prestige):
        for belt in self.belts:
            if belt.get("name") == existing_name:
                belt["current_holder"] = holder or ""
                belt["prestige"] = int(prestige)
                data_loader.save_belts(self.belts)
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


class MatchPanel(ttk.Frame):
    def __init__(self, master, datastore: DataStore):
        super().__init__(master, padding=10)
        self.datastore = datastore
        self._build_widgets()

    def _build_widgets(self):
        ttk.Label(self, text="Match Simulation", font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        ttk.Label(self, text="Face Wrestler").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Heel Wrestler").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(self, text="Match Type").grid(row=3, column=0, sticky="w", pady=2)

        wrestler_names = self.datastore.wrestler_names()
        self.face_var = tk.StringVar(value=wrestler_names[0] if wrestler_names else "")
        self.heel_var = tk.StringVar(value=wrestler_names[1] if len(wrestler_names) > 1 else "")
        self.match_type_var = tk.StringVar()

        self.face_combo = ttk.Combobox(self, values=wrestler_names, textvariable=self.face_var)
        self.heel_combo = ttk.Combobox(self, values=wrestler_names, textvariable=self.heel_var)
        self.match_type_combo = ttk.Combobox(self, values=self._match_types(), textvariable=self.match_type_var, state="readonly")

        if self._match_types():
            self.match_type_var.set(self._match_types()[0])

        simulate_button = ttk.Button(self, text="Simulate", command=self._simulate)

        log_frame = ttk.LabelFrame(self, text="Result Log")
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.face_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.heel_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.match_type_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        simulate_button.grid(row=4, column=0, columnspan=2, pady=8)

        log_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=5)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll.grid(row=0, column=1, sticky="ns")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

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
        if wrestler_names and not self.face_var.get():
            self.face_var.set(wrestler_names[0])
        if len(wrestler_names) > 1 and not self.heel_var.get():
            self.heel_var.set(wrestler_names[1])
        if match_types and not self.match_type_var.get():
            self.match_type_var.set(match_types[0])

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

        face = next((w for w in self.datastore.wrestlers if w.get("name") == face_name), None)
        heel = next((w for w in self.datastore.wrestlers if w.get("name") == heel_name), None)
        if not face or not heel:
            messagebox.showerror("Error", "Could not load wrestler data.")
            return

        assigned_roles = {"Face": [face_name], "Heel": [heel_name]}
        try:
            match = create_match(face, heel, match_type, self.datastore.game_data, assigned_roles)
            log_output = match.simulate()
        except Exception as exc:
            messagebox.showerror("Simulation error", str(exc))
            return

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

        notebook.add(wrestler_tab, text="Wrestlers")
        notebook.add(belt_tab, text="Belts")
        notebook.add(match_tab, text="Match Simulator")
        notebook.pack(fill=tk.BOTH, expand=True)

        self._build_wrestler_tab(wrestler_tab)
        self._build_belt_tab(belt_tab)
        self.match_panel = MatchPanel(match_tab, self.datastore)
        self.match_panel.pack(fill=tk.BOTH, expand=True)

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


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()

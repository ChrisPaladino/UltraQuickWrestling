# match_simulator.py

import tkinter as tk
from tkinter import ttk, scrolledtext
from data_manager import DataManager
from match import Match
from match import Wrestler

class MatchSimulator:
    def __init__(self, master):
        self.master = master
        self.master.title("Ultra Quick Wrestling - Match Simulator")
        self.data_manager = DataManager()
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.master, text="Wrestler 1:").grid(row=0, column=0, padx=5, pady=5)
        self.wrestler1_var = tk.StringVar()
        self.wrestler1_combo = ttk.Combobox(self.master, textvariable=self.wrestler1_var)
        self.wrestler1_combo['values'] = self.data_manager.get_wrestler_names()
        self.wrestler1_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.master, text="Wrestler 2:").grid(row=1, column=0, padx=5, pady=5)
        self.wrestler2_var = tk.StringVar()
        self.wrestler2_combo = ttk.Combobox(self.master, textvariable=self.wrestler2_var)
        self.wrestler2_combo['values'] = self.data_manager.get_wrestler_names()
        self.wrestler2_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.master, text="Match Type:").grid(row=2, column=0, padx=5, pady=5)
        self.match_type_var = tk.StringVar()
        self.match_type_combo = ttk.Combobox(self.master, textvariable=self.match_type_var)
        self.match_type_combo['values'] = ["TV Taping", "PPV", "No DQ", "Cage", "Specialty"]
        self.match_type_combo.grid(row=2, column=1, padx=5, pady=5)

        self.simulate_button = ttk.Button(self.master, text="Simulate Match", command=self.simulate_match)
        self.simulate_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.result_text = scrolledtext.ScrolledText(self.master, width=60, height=20)
        self.result_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def simulate_match(self):
        wrestler1_data = self.data_manager.get_wrestler(self.wrestler1_var.get())
        wrestler2_data = self.data_manager.get_wrestler(self.wrestler2_var.get())
        match_type = self.match_type_var.get()

        if not wrestler1_data or not wrestler2_data or not match_type:
            self.result_text.insert(tk.END, "Please select both wrestlers and a match type.\n")
            return

        wrestler1 = Wrestler(wrestler1_data)
        wrestler2 = Wrestler(wrestler2_data)

        match = Match(wrestler1, wrestler2, match_type, self.data_manager)
        result = match.run_match()

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

        # Update wrestler stats
        self.update_wrestler_stats(wrestler1, wrestler2, match.winner)

    def update_wrestler_stats(self, wrestler1, wrestler2, winner):
        # Implement logic to update wrestler stats after the match
        for wrestler in [wrestler1, wrestler2]:
            if wrestler.name == winner.name:
                wrestler.update_record('win')
            else:
                wrestler.update_record('loss')
            
            self.data_manager.update_wrestler(wrestler)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatchSimulator(root)
    root.mainloop()
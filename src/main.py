import tkinter as tk
from tkinter import ttk
import random
import os
from data_manager import DataManager
from match import Match

class WrestlingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultra Quick Wrestling")

        self.data_manager = DataManager()
        self.wrestlers = self.data_manager.load_wrestlers()
        self.game_data = self.data_manager.load_game_data()

        self.create_widgets()

    def create_widgets(self):
        # Wrestler selection
        tk.Label(self.root, text="Wrestler A:").grid(row=0, column=0, sticky="e")
        self.wrestler_a_var = tk.StringVar()
        self.wrestler_a_menu = ttk.Combobox(self.root, textvariable=self.wrestler_a_var)
        self.wrestler_a_menu['values'] = [w['name'] for w in self.wrestlers]
        self.wrestler_a_menu.grid(row=0, column=1)

        tk.Label(self.root, text="Wrestler B:").grid(row=1, column=0, sticky="e")
        self.wrestler_b_var = tk.StringVar()
        self.wrestler_b_menu = ttk.Combobox(self.root, textvariable=self.wrestler_b_var)
        self.wrestler_b_menu['values'] = [w['name'] for w in self.wrestlers]
        self.wrestler_b_menu.grid(row=1, column=1)

        # Match type
        tk.Label(self.root, text="Match Type:").grid(row=2, column=0, sticky="e")
        self.match_type_var = tk.StringVar()
        self.match_type_menu = ttk.Combobox(self.root, textvariable=self.match_type_var)
        self.match_type_menu['values'] = self.game_data['match_types']
        self.match_type_menu.grid(row=2, column=1)

        # Simulate button
        self.sim_button = tk.Button(self.root, text="Simulate Match", command=self.simulate_match)
        self.sim_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Result box
        self.result_box = tk.Text(self.root, width=60, height=20, wrap="word")
        self.result_box.grid(row=4, column=0, columnspan=2)

    def simulate_match(self):
        name_a = self.wrestler_a_var.get()
        name_b = self.wrestler_b_var.get()
        match_type = self.match_type_var.get()

        if not name_a or not name_b or not match_type:
            self.result_box.delete("1.0", tk.END)
            self.result_box.insert(tk.END, "Please select two wrestlers and a match type.")
            return

        wrestler_a = next(w for w in self.wrestlers if w['name'] == name_a)
        wrestler_b = next(w for w in self.wrestlers if w['name'] == name_b)

        match = Match(wrestler_a, wrestler_b, match_type, self.game_data)
        result = match.resolve_match()

        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, result)

if __name__ == "__main__":
    root = tk.Tk()
    app = WrestlingApp(root)
    root.mainloop()

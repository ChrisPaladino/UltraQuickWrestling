import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import os
from game_logic import GameLogic
from data_manager import DataManager

class WrestlingGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Ultra Quick Wrestling")
        self.master.geometry("600x500")

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_manager = DataManager(base_path)
        self.game_logic = GameLogic(self.data_manager)

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.master, text="Face Wrestler:").grid(row=0, column=0, padx=5, pady=5)
        self.face_var = tk.StringVar()
        self.face_dropdown = ttk.Combobox(self.master, textvariable=self.face_var)
        self.face_dropdown['values'] = self.get_wrestler_names()
        self.face_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.master, text="Heel Wrestler:").grid(row=1, column=0, padx=5, pady=5)
        self.heel_var = tk.StringVar()
        self.heel_dropdown = ttk.Combobox(self.master, textvariable=self.heel_var)
        self.heel_dropdown['values'] = self.get_wrestler_names()
        self.heel_dropdown.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.master, text="Match Type:").grid(row=2, column=0, padx=5, pady=5)
        self.match_type_var = tk.StringVar()
        self.match_type_dropdown = ttk.Combobox(self.master, textvariable=self.match_type_var)
        self.match_type_dropdown['values'] = ["TV Taping", "PPV", "No DQ", "Cage", "Specialty"]
        self.match_type_dropdown.grid(row=2, column=1, padx=5, pady=5)

        self.run_button = ttk.Button(self.master, text="Run Match", command=self.run_match)
        self.run_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.output_box = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=70, height=20)
        self.output_box.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def get_wrestler_names(self):
        return [wrestler['name'] for wrestler in self.data_manager.wrestlers]

    def run_match(self):
        face_name = self.face_var.get()
        heel_name = self.heel_var.get()
        match_type = self.match_type_var.get()

        if not face_name or not heel_name or not match_type:
            self.output_box.insert(tk.END, "Please select both wrestlers and a match type.\n")
            return

        face = self.game_logic.get_wrestler(face_name)
        heel = self.game_logic.get_wrestler(heel_name)

        if not face or not heel:
            self.output_box.insert(tk.END, "One or both wrestlers not found.\n")
            return

        try:
            match = self.game_logic.create_match(face, heel, match_type)
            result = self.game_logic.run_match(match)

            self.output_box.delete(1.0, tk.END)  # Clear previous output
            self.output_box.insert(tk.END, result)
        except Exception as e:
            self.output_box.delete(1.0, tk.END)
            self.output_box.insert(tk.END, f"An error occurred: {str(e)}\n")
            import traceback
            traceback.print_exc()  # This will print the full traceback to the console
            self.output_box.insert(tk.END, f"Check the console for more details.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WrestlingGUI(root)
    root.mainloop()
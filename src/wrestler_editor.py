# wrestler_editor.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import uuid
from data_manager import DataManager
from wrestler import Wrestler

class WrestlerEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Ultra Quick Wrestling - Wrestler Editor")
        self.data_manager = DataManager()
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_tab = ttk.Frame(self.notebook)
        self.edit_tab = ttk.Frame(self.notebook)
        self.delete_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.create_tab, text="Create Wrestler")
        self.notebook.add(self.edit_tab, text="Edit Wrestler")
        self.notebook.add(self.delete_tab, text="Delete Wrestler")

        self.setup_create_tab()
        self.setup_edit_tab()
        self.setup_delete_tab()

    def setup_create_tab(self):
        ttk.Label(self.create_tab, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.create_tab)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.create_tab, text="Persona:").grid(row=1, column=0, padx=5, pady=5)
        self.persona_var = tk.StringVar()
        self.persona_combo = ttk.Combobox(self.create_tab, textvariable=self.persona_var)
        self.persona_combo['values'] = ['Face', 'Heel']
        self.persona_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.create_tab, text="Finisher:").grid(row=2, column=0, padx=5, pady=5)
        self.finisher_entry = ttk.Entry(self.create_tab)
        self.finisher_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.create_tab, text="Overall:").grid(row=3, column=0, padx=5, pady=5)
        self.overall_entry = ttk.Entry(self.create_tab)
        self.overall_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.create_tab, text="Image:").grid(row=4, column=0, padx=5, pady=5)
        self.image_path = tk.StringVar()
        ttk.Entry(self.create_tab, textvariable=self.image_path, state='readonly').grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(self.create_tab, text="Browse", command=self.browse_image).grid(row=4, column=2, padx=5, pady=5)

        attributes = ['size', 'speed', 'strength', 'savvy', 'cheating', 'tech', 'cage', 'object', 'brawl', 'ladder', 'table', 'tag']
        for i, attr in enumerate(attributes):
            ttk.Label(self.create_tab, text=f"{attr.capitalize()}:").grid(row=i+5, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.create_tab)
            entry.grid(row=i+5, column=1, padx=5, pady=5)
            setattr(self, f"{attr}_entry", entry)

        ttk.Button(self.create_tab, text="Create Wrestler", command=self.create_wrestler).grid(row=len(attributes)+5, column=0, columnspan=2, padx=5, pady=5)

    def setup_edit_tab(self):
        ttk.Label(self.edit_tab, text="Select Wrestler:").grid(row=0, column=0, padx=5, pady=5)
        self.edit_wrestler_var = tk.StringVar()
        self.edit_wrestler_combo = ttk.Combobox(self.edit_tab, textvariable=self.edit_wrestler_var)
        self.edit_wrestler_combo['values'] = self.data_manager.get_wrestler_names()
        self.edit_wrestler_combo.grid(row=0, column=1, padx=5, pady=5)
        self.edit_wrestler_combo.bind("<<ComboboxSelected>>", self.load_wrestler_data)

        # Add fields similar to create_tab, but prefixed with 'edit_'
        # Also add fields for wins, losses, injured status, and injury duration

        ttk.Button(self.edit_tab, text="Save Changes", command=self.save_wrestler_changes).grid(row=20, column=0, columnspan=2, padx=5, pady=5)

    def setup_delete_tab(self):
        ttk.Label(self.delete_tab, text="Select Wrestler to Delete:").grid(row=0, column=0, padx=5, pady=5)
        self.delete_wrestler_var = tk.StringVar()
        self.delete_wrestler_combo = ttk.Combobox(self.delete_tab, textvariable=self.delete_wrestler_var)
        self.delete_wrestler_combo['values'] = self.data_manager.get_wrestler_names()
        self.delete_wrestler_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.delete_tab, text="Delete Wrestler", command=self.delete_wrestler).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.webp *.jpg *.jpeg")])
        if file_path:
            self.image_path.set(file_path)

    def handle_image(self, source_path):
        if not source_path:
            return None

        images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'images')
        os.makedirs(images_dir, exist_ok=True)

        _, ext = os.path.splitext(source_path)
        dest_filename = f"{uuid.uuid4()}{ext}"
        dest_path = os.path.join(images_dir, dest_filename)

        with Image.open(source_path) as img:
            img.thumbnail((600, 600))
            img.save(dest_path)

        return dest_filename

    def create_wrestler(self):
        name = self.name_entry.get()
        persona = self.persona_var.get()
        finisher = self.finisher_entry.get()
        overall = int(self.overall_entry.get())
        
        attributes = {}
        for attr in ['size', 'speed', 'strength', 'savvy', 'cheating', 'tech', 'cage', 'object', 'brawl', 'ladder', 'table', 'tag']:
            attributes[attr] = int(getattr(self, f"{attr}_entry").get())

        image = self.handle_image(self.image_path.get())

        wrestler = Wrestler(name, persona, finisher, overall, attributes, image)
        self.data_manager.add_wrestler(wrestler)
        
        messagebox.showinfo("Success", f"Wrestler {name} created successfully!")
        self.update_wrestler_lists()

    def load_wrestler_data(self, event):
        name = self.edit_wrestler_var.get()
        wrestler_data = self.data_manager.get_wrestler(name)
        if wrestler_data:
            wrestler = Wrestler.from_dict(wrestler_data)
            # Populate edit fields with wrestler data
            # ... (implement this part)

    def save_wrestler_changes(self):
        name = self.edit_wrestler_var.get()
        wrestler_data = self.data_manager.get_wrestler(name)
        if wrestler_data:
            # Update wrestler with new data from edit fields
            # ... (implement this part)
            updated_wrestler = Wrestler.from_dict(wrestler_data)
            # Update the wrestler's attributes based on the edit fields
            self.data_manager.update_wrestler(updated_wrestler)
            messagebox.showinfo("Success", f"Wrestler {name} updated successfully!")
            self.update_wrestler_lists()

    def delete_wrestler(self):
        name = self.delete_wrestler_var.get()
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {name}?"):
            self.data_manager.delete_wrestler(name)
            messagebox.showinfo("Success", f"Wrestler {name} deleted successfully!")
            self.update_wrestler_lists()

    def update_wrestler_lists(self):
        wrestler_names = self.data_manager.get_wrestler_names()
        self.edit_wrestler_combo['values'] = wrestler_names
        self.delete_wrestler_combo['values'] = wrestler_names

if __name__ == "__main__":
    root = tk.Tk()
    app = WrestlerEditor(root)
    root.mainloop()
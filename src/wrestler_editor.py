# wrestler_editor.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from data_manager import DataManager
from wrestler import Wrestler

class WrestlerEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Ultra Quick Wrestling - Wrestler Editor")
        self.data_manager = DataManager()
        self.current_image = None
        self.create_widgets()

    def clear_fields(self):
        for attr in ['finisher', 'size', 'speed', 'strength', 'savvy', 'cheating', 'tech',
                     'cage', 'object', 'brawl', 'ladder', 'table', 'tag', 'overall', 'heat',
                     'wins', 'losses', 'ties']:
            getattr(self, f"{attr}_entry").delete(0, tk.END)
        self.persona_entry.set('')
        self.image_label.config(image='')
        self.current_image = None
        self.clear_image()

    def clear_image(self):
        if hasattr(self, 'image_display'):
            self.image_display.destroy()
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        self.current_image = None

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Wrestler Name Dropdown
        ttk.Label(main_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(main_frame, textvariable=self.name_var, width=30)
        self.name_combo['values'] = ['NEW'] + self.data_manager.get_wrestler_names()
        self.name_combo.grid(row=0, column=1, sticky=tk.W)
        self.name_combo.bind("<<ComboboxSelected>>", self.load_wrestler_data)

        # Delete Button
        self.delete_button = ttk.Button(main_frame, text="Delete", command=self.delete_wrestler)
        self.delete_button.grid(row=0, column=2, padx=(10, 0))

        # Finisher
        ttk.Label(main_frame, text="Finisher:").grid(row=1, column=0, sticky=tk.W)
        self.finisher_entry = ttk.Entry(main_frame, width=50)
        self.finisher_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W)

        # Column 1 attributes
        col1_attrs = ['Size', 'Speed', 'Strength', 'Savvy', 'Cheating', 'Tech']
        for i, attr in enumerate(col1_attrs):
            ttk.Label(main_frame, text=f"{attr}:").grid(row=i+2, column=0, sticky=tk.W)
            entry = ttk.Entry(main_frame, width=10)
            entry.grid(row=i+2, column=1, sticky=tk.W)
            setattr(self, f"{attr.lower()}_entry", entry)

        # Column 2 attributes
        col2_attrs = ['Persona', 'Cage', 'Object', 'Brawl', 'Ladder', 'Table', 'Tag']
        for i, attr in enumerate(col2_attrs):
            ttk.Label(main_frame, text=f"{attr}:").grid(row=i+2, column=2, sticky=tk.W, padx=(20, 0))
            if attr == 'Persona':
                widget = ttk.Combobox(main_frame, values=['Face', 'Heel'], width=10)
            else:
                widget = ttk.Entry(main_frame, width=10)
            widget.grid(row=i+2, column=3, sticky=tk.W)
            setattr(self, f"{attr.lower()}_entry", widget)

        # Image section
        self.image_frame = ttk.Frame(main_frame, width=300, height=300, relief="sunken", borderwidth=1)
        self.image_frame.grid(row=0, column=4, rowspan=9, padx=(20, 0), sticky=(tk.N, tk.W, tk.E, tk.S))
        self.image_frame.grid_propagate(False)
        
        self.image_label = ttk.Label(self.image_frame, text="Click to load image")
        self.image_label.bind("<Button-1>", self.load_image)
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        # Bottom row
        ttk.Label(main_frame, text="Overall Rating:").grid(row=9, column=0, sticky=tk.W)
        self.overall_entry = ttk.Entry(main_frame, width=10)
        self.overall_entry.grid(row=9, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Heat:").grid(row=9, column=2, sticky=tk.W, padx=(20, 0))
        self.heat_entry = ttk.Entry(main_frame, width=10)
        self.heat_entry.grid(row=9, column=3, sticky=tk.W)

        ttk.Label(main_frame, text="Wins:").grid(row=10, column=0, sticky=tk.W)
        self.wins_entry = ttk.Entry(main_frame, width=10)
        self.wins_entry.grid(row=10, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Losses:").grid(row=10, column=2, sticky=tk.W, padx=(20, 0))
        self.losses_entry = ttk.Entry(main_frame, width=10)
        self.losses_entry.grid(row=10, column=3, sticky=tk.W)

        ttk.Label(main_frame, text="Ties:").grid(row=11, column=0, sticky=tk.W)
        self.ties_entry = ttk.Entry(main_frame, width=10)
        self.ties_entry.grid(row=11, column=1, sticky=tk.W)

        # Save Button
        self.save_button = ttk.Button(main_frame, text="Save Wrestler", command=self.save_wrestler)
        self.save_button.grid(row=12, column=0, columnspan=4, pady=(10, 0))

    def delete_wrestler(self):
        name = self.name_var.get()
        if name == 'NEW':
            return
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {name}?"):
            self.data_manager.delete_wrestler(name)
            messagebox.showinfo("Success", f"Wrestler {name} deleted successfully!")
            self.update_wrestler_list()
            self.clear_fields()

    def load_image(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if file_path:
            self.load_image_file(file_path)

    def load_image_file(self, file_path):
        image = Image.open(file_path)
        image.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(image)
        
        if hasattr(self, 'image_display'):
            self.image_display.destroy()
        
        self.image_display = ttk.Label(self.image_frame, image=photo)
        self.image_display.image = photo
        self.image_display.place(relx=0.5, rely=0.5, anchor="center")
        
        self.current_image = file_path

    def load_wrestler_data(self, event):
        name = self.name_var.get()
        if name == 'NEW':
            self.clear_fields()
        else:
            wrestler = self.data_manager.get_wrestler(name)
            if wrestler:
                self.populate_fields(wrestler)

    def populate_fields(self, wrestler):
        self.finisher_entry.delete(0, tk.END)
        self.finisher_entry.insert(0, wrestler['finisher'])
        
        for attr in ['size', 'speed', 'strength', 'savvy', 'cheating', 'tech',
                     'cage', 'object', 'brawl', 'ladder', 'table', 'tag']:
            getattr(self, f"{attr}_entry").delete(0, tk.END)
            getattr(self, f"{attr}_entry").insert(0, str(wrestler['attributes'][attr]))
        
        self.persona_entry.set(wrestler['persona'])
        self.overall_entry.delete(0, tk.END)
        self.overall_entry.insert(0, str(wrestler['overall']))
        self.heat_entry.delete(0, tk.END)
        self.heat_entry.insert(0, str(wrestler.get('heat', 0)))
        
        record = wrestler.get('record', {'wins': 0, 'losses': 0, 'draws': 0})
        self.wins_entry.delete(0, tk.END)
        self.wins_entry.insert(0, str(record['wins']))
        self.losses_entry.delete(0, tk.END)
        self.losses_entry.insert(0, str(record['losses']))
        self.ties_entry.delete(0, tk.END)
        self.ties_entry.insert(0, str(record['draws']))

        if wrestler.get('image'):
            self.load_image_file(os.path.join(self.data_manager.base_path, 'data', 'images', wrestler['image']))
        else:
            self.clear_image()

    def save_image(self, wrestler_name):
        if not self.current_image:
            return None

        images_dir = os.path.join(self.data_manager.base_path, 'data', 'images')
        os.makedirs(images_dir, exist_ok=True)

        # Create a filename based on the wrestler's name
        safe_name = "".join([c for c in wrestler_name if c.isalpha() or c.isdigit()]).rstrip()
        filename = f"{safe_name}.webp"
        dest_path = os.path.join(images_dir, filename)

        # If a file with this name already exists, add a number to make it unique
        counter = 1
        while os.path.exists(dest_path):
            filename = f"{safe_name}_{counter}.webp"
            dest_path = os.path.join(images_dir, filename)
            counter += 1

        with Image.open(self.current_image) as img:
            img.thumbnail((600, 600))
            img.save(dest_path, 'WEBP')

        return filename

    def save_wrestler(self):
        name = self.name_var.get()
        if name == 'NEW':
            name = messagebox.askstring("Wrestler Name", "Enter the name for the new wrestler:")
            if not name:
                return

        wrestler_data = {
            'name': name,
            'persona': self.persona_entry.get(),
            'finisher': self.finisher_entry.get(),
            'overall': int(self.overall_entry.get()),
            'attributes': {
                attr: int(getattr(self, f"{attr}_entry").get())
                for attr in ['size', 'speed', 'strength', 'savvy', 'cheating', 'tech',
                             'cage', 'object', 'brawl', 'ladder', 'table', 'tag']
            },
            'heat': int(self.heat_entry.get()),
            'record': {
                'wins': int(self.wins_entry.get()),
                'losses': int(self.losses_entry.get()),
                'draws': int(self.ties_entry.get())
            }
        }

        if self.current_image:
            wrestler_data['image'] = self.save_image(name)

        wrestler = Wrestler(wrestler_data)
        self.data_manager.update_wrestler(wrestler)
        messagebox.showinfo("Success", f"Wrestler {name} saved successfully!")
        self.update_wrestler_list()

    def update_wrestler_list(self):
        self.name_combo['values'] = ['NEW'] + self.data_manager.get_wrestler_names()

if __name__ == "__main__":
    root = tk.Tk()
    app = WrestlerEditor(root)
    root.mainloop()
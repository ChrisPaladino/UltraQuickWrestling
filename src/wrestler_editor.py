# wrestler_editor.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from data_manager import DataManager
from match import Wrestler
import shutil

class WrestlerEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Ultra Quick Wrestling - Wrestler Editor")
        self.data_manager = DataManager()
        self.current_image = None
        self.stats = {}
        self.create_widgets()
        self.update_stats()

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
        wrestler_names = sorted(self.data_manager.get_wrestler_names())
        self.name_combo['values'] = ['NEW'] + wrestler_names
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

        # Stats display
        self.stats_frame = ttk.LabelFrame(main_frame, text="Wrestler Statistics", padding="10")
        self.stats_frame.grid(row=0, column=5, rowspan=12, padx=(20, 0), sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.stats_text = tk.Text(self.stats_frame, width=30, height=20, wrap=tk.WORD, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        # Save Button
        self.save_button = ttk.Button(main_frame, text="Save Wrestler", command=self.save_wrestler)
        self.save_button.grid(row=12, column=0, columnspan=4, pady=(10, 0))

    def delete_wrestler(self):
        name = self.name_var.get()
        if name == 'NEW':
            return
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {name}?"):
            # Get the wrestler data before deletion
            wrestler = self.data_manager.get_wrestler(name)
            
            # Delete the wrestler from the data manager
            self.data_manager.delete_wrestler(name)
            
            # Delete the associated image if it exists
            if wrestler and 'image' in wrestler:
                image_path = os.path.join(self.data_manager.base_path, 'data', 'images', wrestler['image'])
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        print(f"Failed to delete image: {str(e)}")
            
            messagebox.showinfo("Success", f"Wrestler {name} deleted successfully!")
            self.update_wrestler_list()
            self.clear_fields()
            self.update_stats()

    def display_stats(self):
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete('1.0', tk.END)
        
        for attr, values in self.stats.items():
            self.stats_text.insert(tk.END, f"{attr.capitalize()}:\n")
            self.stats_text.insert(tk.END, f"  Min: {values['min']}\n")
            self.stats_text.insert(tk.END, f"  Max: {values['max']}\n")
            self.stats_text.insert(tk.END, f"  Avg: {values['avg']:.2f}\n\n")
        
        self.stats_text.config(state=tk.DISABLED)

    def load_image(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if file_path:
            self.load_image_file(file_path)

    def load_image_file(self, file_path):
        if hasattr(self, 'image_display'):
            self.image_display.destroy()

        image = Image.open(file_path)
        image.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(image)
        
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

        safe_name = "".join([c for c in wrestler_name if c.isalpha() or c.isdigit()]).rstrip()
        filename = f"{safe_name}.webp"
        dest_path = os.path.join(images_dir, filename)

        counter = 1
        while os.path.exists(dest_path):
            filename = f"{safe_name}_{counter}.webp"
            dest_path = os.path.join(images_dir, filename)
            counter += 1

        try:
            with Image.open(self.current_image) as img:
                img.thumbnail((600, 600))
                img.save(dest_path, 'WEBP')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            return None

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
            'overall': self.safe_int(self.overall_entry.get()),
            'attributes': {
                attr: self.safe_int(getattr(self, f"{attr}_entry").get())
                for attr in ['size', 'speed', 'strength', 'savvy', 'cheating', 'tech',
                            'cage', 'object', 'brawl', 'ladder', 'table', 'tag']
            },
            'heat': self.safe_int(self.heat_entry.get()),
            'record': {
                'wins': self.safe_int(self.wins_entry.get()),
                'losses': self.safe_int(self.losses_entry.get()),
                'draws': self.safe_int(self.ties_entry.get())
            }
        }

        if self.current_image:
            wrestler_data['image'] = self.save_image(name)

        wrestler = Wrestler(wrestler_data)
        self.data_manager.update_wrestler(wrestler)
        messagebox.showinfo("Success", f"Wrestler {name} saved successfully!")
        self.update_wrestler_list()
        self.update_stats()

    def safe_int(self, value):
        try:
            return int(value)
        except ValueError:
            return 0

    def update_stats(self):
        wrestlers = self.data_manager.wrestlers
        attributes = ['size', 'speed', 'strength', 'savvy', 'cheating', 'tech',
                    'cage', 'object', 'brawl', 'ladder', 'table', 'tag', 'overall']

        self.stats = {attr: {'min': float('inf'), 'max': float('-inf'), 'sum': 0} for attr in attributes}

        for wrestler in wrestlers:
            for attr in attributes:
                if attr == 'overall':
                    value = wrestler.get('overall', 0)
                else:
                    value = wrestler.get('attributes', {}).get(attr, 0)
                value = int(value)  # Ensure the value is an integer
                self.stats[attr]['min'] = min(self.stats[attr]['min'], value)
                self.stats[attr]['max'] = max(self.stats[attr]['max'], value)
                self.stats[attr]['sum'] += value

        for attr in attributes:
            self.stats[attr]['avg'] = self.stats[attr]['sum'] / len(wrestlers) if wrestlers else 0

        self.display_stats()

    def update_wrestler_list(self):
        wrestler_names = sorted(self.data_manager.get_wrestler_names())
        self.name_combo['values'] = ['NEW'] + wrestler_names

if __name__ == "__main__":
    root = tk.Tk()
    app = WrestlerEditor(root)
    root.mainloop()
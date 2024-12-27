import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import os

class AppuntiPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.config = self.load_config()
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
        self.create_content()
    
    def load_config(self):
        config = configparser.ConfigParser()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        config_path = os.path.join(parent_dir, 'config.ini')
        config.read(config_path)
        return config
    
    def create_content(self):
        # Frame per i bottoni
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Stile per i bottoni
        button_style = {'width': 15, 'padding': 5}
        
        # Bottoni di gestione
        ttk.Button(button_frame, text="INSERISCI", command=self.insert_note, **button_style).pack(side="left", padx=5)
        ttk.Button(button_frame, text="MODIFICA", command=self.edit_note, **button_style).pack(side="left", padx=5)
        ttk.Button(button_frame, text="CANCELLA", command=self.delete_note, **button_style).pack(side="left", padx=5)
        
        # Contenitore principale con scrollbar
        self.create_notes_view()
    
    def create_notes_view(self):
        if hasattr(self, 'notes_frame'):
            self.notes_frame.destroy()
            
        self.notes_frame = ttk.Frame(self)
        self.notes_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(self.notes_frame)
        scrollbar = ttk.Scrollbar(self.notes_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame principale per il contenuto
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Stili per i testi
        title_style = {'font': ('Arial', 12, 'bold')}
        value_style = {'font': ('Arial', 12), 'wraplength': 600}
        
        # Visualizzazione degli appunti
        if 'Appunti' in self.config:
            for key, value in self.config['Appunti'].items():
                pair_frame = ttk.Frame(main_frame)
                pair_frame.pack(fill="x", pady=10)
                
                ttk.Label(pair_frame, text=f"{key.upper()}:", **title_style).pack(anchor="w")
                ttk.Label(pair_frame, text=value, justify="left", **value_style).pack(anchor="w", padx=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def insert_note(self):
        dialog = NoteDialog(self, "Inserisci Nuovo Appunto")
        if dialog.result:
            key, value = dialog.result
            if 'Appunti' not in self.config:
                self.config['Appunti'] = {}
            self.config['Appunti'][key] = value
            self.save_config()
            self.create_notes_view()
    
    def edit_note(self):
        if 'Appunti' not in self.config or not self.config['Appunti']:
            messagebox.showwarning("Attenzione", "Non ci sono appunti da modificare!")
            return
            
        # Dialog per selezionare l'appunto da modificare
        select_dialog = SelectNoteDialog(self, "Seleziona Appunto da Modificare", 
                                       list(self.config['Appunti'].keys()))
        if select_dialog.result:
            key = select_dialog.result
            value = self.config['Appunti'][key]
            
            # Dialog per modificare l'appunto
            edit_dialog = NoteDialog(self, "Modifica Appunto", key, value)
            if edit_dialog.result:
                new_key, new_value = edit_dialog.result
                if new_key != key:
                    del self.config['Appunti'][key]
                self.config['Appunti'][new_key] = new_value
                self.save_config()
                self.create_notes_view()
    
    def delete_note(self):
        if 'Appunti' not in self.config or not self.config['Appunti']:
            messagebox.showwarning("Attenzione", "Non ci sono appunti da cancellare!")
            return
            
        # Dialog per selezionare l'appunto da cancellare
        select_dialog = SelectNoteDialog(self, "Seleziona Appunto da Cancellare", 
                                       list(self.config['Appunti'].keys()))
        if select_dialog.result:
            key = select_dialog.result
            if messagebox.askyesno("Conferma", f"Sei sicuro di voler cancellare l'appunto '{key}'?"):
                del self.config['Appunti'][key]
                self.save_config()
                self.create_notes_view()
    
    def save_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

class NoteDialog:
    def __init__(self, parent, title, key="", value=""):
        self.result = None
        
        # Creazione della finestra di dialogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Frame per il contenuto
        content_frame = ttk.Frame(self.dialog, padding=10)
        content_frame.pack(fill="both", expand=True)
        
        # Campi di input
        ttk.Label(content_frame, text="Parametro:").pack(anchor="w")
        self.key_entry = ttk.Entry(content_frame, width=50)
        self.key_entry.insert(0, key)
        self.key_entry.pack(fill="x", pady=(0, 10))
        
        ttk.Label(content_frame, text="Valore:").pack(anchor="w")
        self.value_text = tk.Text(content_frame, height=10, width=50)
        self.value_text.insert("1.0", value)
        self.value_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Bottoni
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Annulla", command=self.dialog.destroy).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Salva", command=self.save).pack(side="right")
        
        self.dialog.wait_window()
    
    def save(self):
        key = self.key_entry.get().strip()
        value = self.value_text.get("1.0", "end-1c").strip()
        
        if not key or not value:
            messagebox.showwarning("Errore", "Entrambi i campi sono obbligatori!")
            return
        
        self.result = (key, value)
        self.dialog.destroy()

class SelectNoteDialog:
    def __init__(self, parent, title, options):
        self.result = None
        
        # Creazione della finestra di dialogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Frame per il contenuto
        content_frame = ttk.Frame(self.dialog, padding=10)
        content_frame.pack(fill="both", expand=True)
        
        # Lista degli appunti
        self.listbox = tk.Listbox(content_frame, width=50)
        self.listbox.pack(fill="both", expand=True, pady=(0, 10))
        
        for option in options:
            self.listbox.insert(tk.END, option)
        
        # Bottoni
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Annulla", command=self.dialog.destroy).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Seleziona", command=self.select).pack(side="right")
        
        self.dialog.wait_window()
    
    def select(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Errore", "Seleziona un appunto!")
            return
        
        self.result = self.listbox.get(selection[0])
        self.dialog.destroy() 
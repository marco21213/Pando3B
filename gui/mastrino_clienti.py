import tkinter as tk
from tkinter import ttk

class MastrinoClientiPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Titolo della pagina
        title = tk.Label(self, text="Mastrino Clienti", font=("Helvetica", 16, "bold"))
        title.pack(pady=20)
        
        # Contenuto specifico della pagina
        self.create_content()
    
    def create_content(self):
        # Qui inserisci il contenuto specifico della pagina
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Esempio di contenuto
        ttk.Label(content_frame, text="Gestione Mastrino Clienti").pack() 
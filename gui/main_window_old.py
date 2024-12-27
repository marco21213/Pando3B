import sys
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import locale
from gui.download import DownloadPage
from gui.mastrino_clienti import MastrinoClientiPage
from gui.mastrino_fornitori import MastrinoFornitoriPage
from gui.inserisci import InserisciPage
from gui.crea_categoria import CreaCategoriaPage
from gui.ricerca import RicercaPage
from gui.appunti import AppuntiPage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class PandoSoftware:
    def __init__(self, root):
        self.root = root
        self.root.title("PandoInvoice Desktop")
        self.root.minsize(800, 600)
        
        # Dizionario per tenere traccia dei pulsanti di navigazione
        self.nav_buttons = {}
        
        # Layout principale
        self.create_layout()
        
    def create_layout(self):
        # Container principale
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # Frame navigazione (colonna sinistra)
        self.nav_frame = tk.Frame(main_container, width=200, bg="#f0f0f0")
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False)
        
        # Frame contenuto (colonna destra)
        self.content_frame = tk.Frame(main_container, bg="white")
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Creazione menu di navigazione
        self.create_nav_menu()
        
        # Mostra la pagina iniziale (optional)
        self.show_page("download")

    def create_nav_menu(self):
        # Stile per le categorie
        categoria_style = {"bg": "#4a90e2", "fg": "white", "pady": 5, "padx": 10}
        # Stile per le voci di menu
        voce_style = {"bg": "#f0f0f0", "pady": 3, "padx": 20, "relief": "flat", "anchor": "w", "width": 20}
        
        # CONTABILITÀ
        tk.Label(self.nav_frame, text="CONTABILITA'", **categoria_style).pack(fill="x")
        
        self.nav_buttons["download"] = tk.Button(
            self.nav_frame, 
            text="DOWNLOAD", 
            command=lambda: self.show_page("download"), 
            **voce_style
        )
        self.nav_buttons["download"].pack(fill="x")
        
        self.nav_buttons["mastrino_clienti"] = tk.Button(
            self.nav_frame, 
            text="MASTRINO CLIENTI", 
            command=lambda: self.show_page("mastrino_clienti"), 
            **voce_style
        )
        self.nav_buttons["mastrino_clienti"].pack(fill="x")
        
        self.nav_buttons["mastrino_fornitori"] = tk.Button(
            self.nav_frame, 
            text="MASTR. FORNITORI", 
            command=lambda: self.show_page("mastrino_fornitori"), 
            **voce_style
        )
        self.nav_buttons["mastrino_fornitori"].pack(fill="x")
        
        # LABORATORIO
        tk.Label(self.nav_frame, text="LABORATORIO", **categoria_style).pack(fill="x")
        
        self.nav_buttons["inserisci"] = tk.Button(
            self.nav_frame, 
            text="INSERISCI", 
            command=lambda: self.show_page("inserisci"), 
            **voce_style
        )
        self.nav_buttons["inserisci"].pack(fill="x")
        
        self.nav_buttons["crea_categoria"] = tk.Button(
            self.nav_frame, 
            text="CREA CATEGORIA", 
            command=lambda: self.show_page("crea_categoria"), 
            **voce_style
        )
        self.nav_buttons["crea_categoria"].pack(fill="x")
        
        self.nav_buttons["ricerca"] = tk.Button(
            self.nav_frame, 
            text="RICERCA", 
            command=lambda: self.show_page("ricerca"), 
            **voce_style
        )
        self.nav_buttons["ricerca"].pack(fill="x")
        
        self.nav_buttons["appunti"] = tk.Button(
            self.nav_frame, 
            text="APPUNTI", 
            command=lambda: self.show_page("appunti"), 
            **voce_style
        )
        self.nav_buttons["appunti"].pack(fill="x")

    def show_page(self, page_name):
        # Pulisce il frame del contenuto
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Reset colore di tutti i pulsanti
        for button in self.nav_buttons.values():
            button.configure(bg="#f0f0f0")
        
        # Evidenzia il pulsante attivo
        if page_name in self.nav_buttons:
            self.nav_buttons[page_name].configure(bg="#e0e0e0")
        
        # Carica la pagina appropriata
        if page_name == "download":
            page = DownloadPage(self.content_frame)
        elif page_name == "mastrino_clienti":
            page = MastrinoClientiPage(self.content_frame)
        elif page_name == "mastrino_fornitori":
            page = MastrinoFornitoriPage(self.content_frame)
        elif page_name == "inserisci":
            page = InserisciPage(self.content_frame)
        elif page_name == "crea_categoria":
            page = CreaCategoriaPage(self.content_frame)
        elif page_name == "ricerca":
            page = RicercaPage(self.content_frame)
        elif page_name == "appunti":
            page = AppuntiPage(self.content_frame)
        
        page.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = PandoSoftware(root)
    root.mainloop() 
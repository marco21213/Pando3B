import tkinter as tk
from tkinter import ttk, font, messagebox
import configparser
import os
from PIL import Image, ImageTk
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AggiornaCredenziali import aggiorna_credenziali


class DownloadPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.config = self.load_config()
        
        # Stili per uniformità
        self.label_style = {'font': ('Arial', 10, 'bold')}
        
        # Creiamo un font personalizzato per le intestazioni
        self.section_header_font = font.Font(family='Arial', size=14, weight='bold')
        
        # Creazione del contenitore principale con scrollbar
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout principale
        self.create_download_rapido_box()
        self.create_seleziona_periodo_box()
        self.create_credenziali_box()
        
        # Pack del canvas e scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_icon(self, icon_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, 'icons', icon_name)
        image = Image.open(icon_path)
        image = image.resize((64, 64), Image.Resampling.LANCZOS)  # Icone più grandi
        return ImageTk.PhotoImage(image)
        
    def load_config(self):
        config = configparser.ConfigParser()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        config_path = os.path.join(parent_dir, 'config.ini')
        config.read(config_path)
        return config
        
    def create_download_rapido_box(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="DOWNLOAD RAPIDO")
        frame.configure(labelwidget=tk.Label(frame, text="DOWNLOAD RAPIDO", font=self.section_header_font))
        frame.pack(fill="x", padx=10, pady=10)
        
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill="x", padx=5, pady=5)
        
        icon = self.load_icon('fast-download.png')
        icon_label = ttk.Label(content_frame, image=icon)
        icon_label.image = icon
        icon_label.pack(side="left", padx=(5, 15))
        
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(side="left", fill="x", expand=True)
        
        ultima_data = self.config.get("Profilo", "aggiornamento", fallback="Data non disponibile")
        ttk.Label(text_frame, text=f"Ultimo aggiornamento: {ultima_data}",
                 foreground='#0066CC', **self.label_style).pack(anchor="w", pady=5)
        
        ttk.Button(text_frame, text="ESEGUI",
                  command=lambda: subprocess.run(["python", "ScaricaRapido.py"])).pack(anchor="w", pady=5)
        
    def create_seleziona_periodo_box(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="SELEZIONA PERIODO")
        frame.configure(labelwidget=tk.Label(frame, text="SELEZIONA PERIODO", font=self.section_header_font))
        frame.pack(fill="x", padx=10, pady=20)
        
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill="x", padx=5, pady=5)
        
        icon = self.load_icon('sel-periodo.png')
        icon_label = ttk.Label(content_frame, image=icon)
        icon_label.image = icon
        icon_label.pack(side="left", padx=(5, 15))
        
        form_frame = ttk.Frame(content_frame)
        form_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(form_frame, text="DAL:", **self.label_style).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="AL:", **self.label_style).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="TIPO:", **self.label_style).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        combo = ttk.Combobox(form_frame, values=["Data emissione", "Data ricezione"], width=27)
        combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        combo.set("Data emissione")
        
        ttk.Button(form_frame, text="ESEGUI",
                   command=lambda: subprocess.run(["python", "ScaricaPeriodo.py"])).grid(row=3, column=1, pady=10, sticky="w")
        
    def create_credenziali_box(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="CREDENZIALI")
        frame.configure(labelwidget=tk.Label(frame, text="CREDENZIALI", font=self.section_header_font))
        frame.pack(fill="x", padx=10, pady=10)
        
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill="x", padx=5, pady=5)
        
        icon = self.load_icon('login.png')
        icon_label = ttk.Label(content_frame, image=icon)
        icon_label.image = icon
        icon_label.pack(side="left", padx=(5, 15))
        
        form_frame = ttk.Frame(content_frame)
        form_frame.pack(side="left", fill="x", expand=True)
        
        codice_fiscale = self.config.get('Credenziali', 'codicefiscale', fallback='')
        pin = self.config.get('Credenziali', 'pin', fallback='')
        password = self.config.get('Credenziali', 'password', fallback='')
        
        ttk.Label(form_frame, text="CODICE FISCALE:", **self.label_style).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        cf_entry = ttk.Entry(form_frame, width=30)
        cf_entry.insert(0, codice_fiscale)
        cf_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="PIN:", **self.label_style).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        pin_entry = ttk.Entry(form_frame, width=30,)
        pin_entry.insert(0, pin)
        pin_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="PASSWORD:", **self.label_style).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        pwd_entry = ttk.Entry(form_frame, width=30, show="*")
        pwd_entry.insert(0, password)
        pwd_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(form_frame, text="AGGIORNA",
                   command=lambda: aggiorna_credenziali(cf_entry.get(), pin_entry.get(), pwd_entry.get())).grid(row=3, column=1, pady=10, sticky="w")

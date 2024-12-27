import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from datetime import datetime

class InserisciPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_inputs = []
        self.quantita_inputs = []
        self.create_content()
    
    def create_content(self):
        # Contenitore principale con scrollbar
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # INFORMAZIONI GENERALI
        info_frame = ttk.LabelFrame(scrollable_frame, text="INFORMAZIONI GENERALI:", padding=10)
        info_frame.pack(fill="x", padx=20, pady=5)
        
        # Form layout
        form_frame = ttk.Frame(info_frame)
        form_frame.pack(fill="x", expand=True)
        
        # Stile per le label
        label_style = {'font': ('Arial', 10, 'bold')}
        
        # Categoria
        ttk.Label(form_frame, text="CATEGORIA:", **label_style).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.categoria_combo = ttk.Combobox(form_frame, width=30)
        self.load_categories()
        self.categoria_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Altri campi
        fields = [
            ("CODICE:", ttk.Entry(form_frame, width=30)),
            ("DATA:", ttk.Entry(form_frame, width=30)),
            ("NOME:", ttk.Entry(form_frame, width=30)),
            ("RIFERIMENTO:", ttk.Entry(form_frame, width=30))
        ]
        
        self.field_widgets = {}  # Per accedere ai widget più tardi
        
        for i, (label_text, widget) in enumerate(fields, start=1):
            ttk.Label(form_frame, text=label_text, **label_style).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            widget.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.field_widgets[label_text] = widget
            
        # Imposta data corrente
        self.field_widgets["DATA:"].insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Avviso caratteri non ammessi
        warning_chars_label = ttk.Label(
            form_frame, 
            text="ATTENZIONE: Non utilizzare i seguenti caratteri:\nˆ ~ \" # % & * : < > ? / \\ { | }",
            font=('Arial', 9, 'italic'),
            foreground='red'
        )
        warning_chars_label.grid(row=5, column=0, columnspan=2, padx=5, pady=(10,0), sticky="w")
        
        # COMPOSIZIONE
        comp_frame = ttk.LabelFrame(scrollable_frame, text="COMPOSIZIONE:", padding=10)
        comp_frame.pack(fill="x", padx=20, pady=5)
        
        # Aggiunta avviso per i decimali
        warning_frame = ttk.Frame(comp_frame)
        warning_frame.pack(fill="x", padx=5, pady=(0, 10))
        warning_label = ttk.Label(warning_frame, 
                                text="Nota: utilizzare il punto (.) per i decimali. Esempio: 35.5",
                                font=('Arial', 9, 'italic'),
                                foreground='red')
        warning_label.pack(side="left")
        
        # Grid per colori e quantità
        grid_frame = ttk.Frame(comp_frame)
        grid_frame.pack(fill="x", expand=True)
        
        for i in range(7):
            # Label e input per il colore
            ttk.Label(grid_frame, text=f"COLORE {i+1}:", **label_style).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            base_input = ttk.Entry(grid_frame, width=30)
            base_input.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.base_inputs.append(base_input)
            
            # Label e input per la quantità
            ttk.Label(grid_frame, text="Q.TA:", **label_style).grid(row=i, column=2, padx=5, pady=5, sticky="e")
            quantita_input = ttk.Entry(grid_frame, width=10)
            quantita_input.grid(row=i, column=3, padx=5, pady=5, sticky="w")
            self.quantita_inputs.append(quantita_input)
        
        # Bottoni
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(button_frame, text="RESET", command=self.reset_fields).pack(side="left", padx=5)
        ttk.Button(button_frame, text="INSERISCI", command=self.inserisci_dati).pack(side="left", padx=5)
        
        # Pack finale del canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_categories(self):
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            cursor.execute("SELECT descrizione FROM categoria")
            categorie = cursor.fetchall()
            self.categoria_combo['values'] = [cat[0] for cat in categorie]
            if self.categoria_combo['values']:
                self.categoria_combo.set(self.categoria_combo['values'][0])
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Errore di connessione", f"Errore: {e}")
            
    def reset_fields(self):
        if self.categoria_combo['values']:
            self.categoria_combo.set(self.categoria_combo['values'][0])
        
        for widget in self.field_widgets.values():
            if widget != self.field_widgets["DATA:"]:
                widget.delete(0, tk.END)
                
        self.field_widgets["DATA:"].delete(0, tk.END)
        self.field_widgets["DATA:"].insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        for input_widget in self.base_inputs + self.quantita_inputs:
            input_widget.delete(0, tk.END)
            
    def inserisci_dati(self):
        # Caratteri non ammessi
        forbidden_chars = ['ˆ', '~', '"', '#', '%', '&', '*', ':', '<', '>', '?', '/', '\\', '{', '|', '}']
        
        # Conversione in maiuscolo di tutti i valori stringa
        categoria_val = self.categoria_combo.get().upper()
        codice_val = self.field_widgets["CODICE:"].get().upper()
        data_val = self.field_widgets["DATA:"].get()  # La data non va convertita
        nome_val = self.field_widgets["NOME:"].get().upper()
        riferimento_val = self.field_widgets["RIFERIMENTO:"].get().upper()
        
        # Controllo campi obbligatori
        if not codice_val or not nome_val:
            messagebox.showwarning("Errore", "Compila tutti i campi obbligatori!")
            return
        
        # Controllo caratteri proibiti in codice e nome
        for field, value in [("Codice", codice_val), ("Nome", nome_val)]:
            for char in forbidden_chars:
                if char in value:
                    messagebox.showwarning(
                        "Errore caratteri", 
                        f"Il campo {field} contiene caratteri non ammessi.\n"
                        f"Caratteri vietati: ˆ ~ \" # % & * : < > ? / \\ {{ | }}"
                    )
                    return
        
        # Controllo formato decimali
        for quantita_input in self.quantita_inputs:
            quantita_val = quantita_input.get()
            if quantita_val:  # se il campo non è vuoto
                if ',' in quantita_val:
                    messagebox.showwarning(
                        "Errore formato", 
                        "Utilizzare il punto (.) per i decimali invece della virgola (,).\n"
                        "Esempio: 35.5 invece di 35,5"
                    )
                    return
                try:
                    float(quantita_val)
                except ValueError:
                    messagebox.showwarning(
                        "Errore formato",
                        "Le quantità devono essere numeri validi.\n"
                        "Esempio: 35.5"
                    )
                    return
        
        # Conversione in maiuscolo dei valori dei colori
        colori_values = [(base_input.get().upper(), quantita_input.get()) 
                        for base_input, quantita_input 
                        in zip(self.base_inputs, self.quantita_inputs)]
            
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            
            # Controllo codice duplicato
            cursor.execute("SELECT COUNT(*) FROM colore WHERE codice = ?", (codice_val,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Errore", "Esiste già un record con questo codice!")
                conn.close()
                return
            
            cursor.execute("""
                INSERT INTO colore (codice, data, nome, riferimento, categoria_id) 
                VALUES (?, ?, ?, ?, (SELECT id FROM categoria WHERE descrizione = ?))
                """, (codice_val, data_val, nome_val, riferimento_val, categoria_val))
                
            colore_id = cursor.lastrowid
            
            for base_val, quantita_val in colori_values:
                if base_val and quantita_val:
                    cursor.execute("""
                        INSERT INTO righecolore (base, quantita, colore_id) 
                        VALUES (?, ?, ?)
                        """, (base_val, quantita_val, colore_id))
                        
            conn.commit()
            conn.close()
            messagebox.showinfo("Successo", "Dati inseriti con successo!")
            self.reset_fields()
            
        except sqlite3.Error as e:
            messagebox.showerror("Errore di connessione", f"Errore: {e}")

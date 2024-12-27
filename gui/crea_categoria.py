import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox, simpledialog

class CreaCategoriaPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
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
        
        # Stile per le label
        label_style = {'font': ('Arial', 10, 'bold')}
        
        # INSERIMENTO NUOVA CATEGORIA
        inserimento_frame = ttk.LabelFrame(scrollable_frame, text="INSERISCI NUOVA CATEGORIA:", padding=10)
        inserimento_frame.pack(fill="x", padx=20, pady=5)
        
        # Form layout
        form_frame = ttk.Frame(inserimento_frame)
        form_frame.pack(fill="x", expand=True)
        
        # Nome Categoria
        ttk.Label(form_frame, text="NOME CATEGORIA:", **label_style).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.nome_categoria_entry = ttk.Entry(form_frame, width=30)
        self.nome_categoria_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Informazioni
        ttk.Label(form_frame, text="INFORMAZIONI:", **label_style).grid(row=1, column=0, padx=5, pady=5, sticky="ne")
        self.informazioni_text = tk.Text(form_frame, width=30, height=4)
        self.informazioni_text.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Bottoni
        button_frame = ttk.Frame(inserimento_frame)
        button_frame.pack(fill="x", padx=5, pady=10)
        
        ttk.Button(button_frame, text="RESET", command=self.reset_fields).pack(side="left", padx=5)
        ttk.Button(button_frame, text="INSERISCI", command=self.inserisci_categoria).pack(side="left", padx=5)
        ttk.Button(button_frame, text="MODIFICA", command=self.modifica_categoria).pack(side="left", padx=5)
        
        # LISTA CATEGORIE ESISTENTI
        lista_frame = ttk.LabelFrame(scrollable_frame, text="CATEGORIE ESISTENTI:", padding=10)
        lista_frame.pack(fill="x", padx=20, pady=5)
        
        # Treeview per mostrare le categorie
        self.tree = ttk.Treeview(lista_frame, columns=("Nome", "Informazioni"), show="headings")
        self.tree.heading("Nome", text="NOME CATEGORIA")
        self.tree.heading("Informazioni", text="INFORMAZIONI")
        self.tree.pack(fill="both", expand=True)
        
        # Doppio click per selezionare categoria
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Carica le categorie esistenti
        self.carica_categorie()
        
        # Pack finale del canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def reset_fields(self):
        self.nome_categoria_entry.delete(0, tk.END)
        self.informazioni_text.delete('1.0', tk.END)
    
    def inserisci_categoria(self):
        # Conversione in maiuscolo dei valori
        nome_categoria = self.nome_categoria_entry.get().upper().strip()
        informazioni = self.informazioni_text.get('1.0', tk.END).strip().upper()
        
        # Controlli di validazione
        if not nome_categoria or not informazioni:
            messagebox.showwarning("Errore", "Compila tutti i campi!")
            return
        
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            
            # Controllo se la categoria esiste già
            cursor.execute("SELECT * FROM categoria WHERE descrizione = ?", (nome_categoria,))
            if cursor.fetchone():
                messagebox.showwarning("Errore", "Una categoria con questo nome esiste già!")
                conn.close()
                return
            
            # Inserimento nuova categoria
            cursor.execute("INSERT INTO categoria (descrizione, informazioni) VALUES (?, ?)", 
                           (nome_categoria, informazioni))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Successo", "Categoria inserita con successo!")
            
            # Aggiorna la lista delle categorie e resetta i campi
            self.carica_categorie()
            self.reset_fields()
            
        except sqlite3.Error as e:
            messagebox.showerror("Errore di connessione", f"Errore: {e}")
    
    def carica_categorie(self):
        # Pulisci la treeview esistente
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            
            # Carica tutte le categorie
            cursor.execute("SELECT descrizione, informazioni FROM categoria")
            categorie = cursor.fetchall()
            
            # Popola la treeview
            for categoria in categorie:
                self.tree.insert("", "end", values=categoria)
            
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Errore di connessione", f"Errore: {e}")
    
    def on_double_click(self, event):
        # Ottiene la riga selezionata
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        # Recupera i valori della riga
        values = self.tree.item(selected_item[0])['values']
        
        # Imposta i campi per la modifica
        self.nome_categoria_entry.delete(0, tk.END)
        self.nome_categoria_entry.insert(0, values[0])
        
        self.informazioni_text.delete('1.0', tk.END)
        self.informazioni_text.insert('1.0', values[1])
    
    def modifica_categoria(self):
        # Recupera i valori attuali
        nome_attuale = self.nome_categoria_entry.get().upper().strip()
        nuove_informazioni = self.informazioni_text.get('1.0', tk.END).strip().upper()
        
        # Controlli di validazione
        if not nome_attuale or not nuove_informazioni:
            messagebox.showwarning("Errore", "Seleziona una categoria e compila tutti i campi!")
            return
        
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            
            # Aggiorna le informazioni della categoria
            cursor.execute("""
                UPDATE categoria 
                SET informazioni = ? 
                WHERE descrizione = ?
            """, (nuove_informazioni, nome_attuale))
            
            # Verifica se l'aggiornamento ha avuto successo
            if cursor.rowcount == 0:
                messagebox.showwarning("Errore", "Categoria non trovata!")
                conn.close()
                return
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Successo", "Categoria modificata con successo!")
            
            # Aggiorna la lista delle categorie
            self.carica_categorie()
            self.reset_fields()
            
        except sqlite3.Error as e:
            messagebox.showerror("Errore di connessione", f"Errore: {e}")

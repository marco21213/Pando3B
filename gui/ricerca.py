import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from CompilaWord import fill_and_save_word

class RicercaPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_content()

    def create_content(self):
        # Frame principale
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Frame per la ricerca
        search_frame = ttk.LabelFrame(main_frame, text="Ricerca", padding=10)
        search_frame.pack(fill="x", pady=(0, 10))

        # Grid per i campi di ricerca
        grid = ttk.Frame(search_frame)
        grid.pack(fill="x", padx=5, pady=5)

        # Stile per le label
        label_style = {'font': ('Arial', 10, 'bold')}

        # Campi di ricerca
        ttk.Label(grid, text="Codice:", **label_style).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.codice_search = ttk.Entry(grid, width=30)
        self.codice_search.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(grid, text="Descrizione:", **label_style).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.desc_search = ttk.Entry(grid, width=30)
        self.desc_search.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(grid, text="Categoria:", **label_style).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.cat_search = ttk.Combobox(grid, width=27, state="readonly")
        self.load_categories()
        self.cat_search.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(grid, text="Riferimento:", **label_style).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.rif_search = ttk.Entry(grid, width=30)
        self.rif_search.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Frame per i bottoni di ricerca
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        # Bottoni
        ttk.Button(button_frame, text="Reset", command=self.reset_search).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cerca", command=self.search_records).pack(side="left", padx=5)

        # Frame per i bottoni azioni
        action_buttons_frame = ttk.Frame(main_frame)
        action_buttons_frame.pack(pady=10)

        # Bottone per visualizzare i dettagli
        detail_button = ttk.Button(action_buttons_frame, text="Mostra Dettagli", command=self.show_details)
        detail_button.pack(side="left", padx=5)

        # Bottone per eliminare il record
        delete_button = ttk.Button(action_buttons_frame, text="Elimina", 
                                    command=self.delete_record,
                                    style="Delete.TButton")
        delete_button.pack(side="left", padx=5)

        # Stile per il bottone elimina (rosso)
        style = ttk.Style()
        style.configure("Delete.TButton",
                        foreground="red",
                        font=('Arial', 10, 'bold'))

        # Creazione della tabella con scrolling
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)

        # Scrollbar per la tabella
        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")

        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        # Creazione della tabella
        self.table = ttk.Treeview(table_frame, 
                                   columns=("Codice", "Descrizione", "Categoria", "Riferimento"),
                                   show="headings",
                                   yscrollcommand=scroll_y.set,
                                   xscrollcommand=scroll_x.set)

        # Configurazione delle scrollbar
        scroll_y.config(command=self.table.yview)
        scroll_x.config(command=self.table.xview)

        # Configurazione delle colonne
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=150)

        self.table.pack(fill="both", expand=True)

        # Popolamento iniziale della tabella
        self.populate_table()

    def delete_record(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Attenzione", "Seleziona un record da eliminare.")
            return

        # Conferma eliminazione
        if not messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare il record selezionato?"):
            return

        item_values = self.table.item(selected_item[0])['values']
        codice = item_values[0]

        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()

            # Recupera l'ID del record per eliminare le righe associate
            cursor.execute("SELECT id FROM colore WHERE codice = ?", (codice,))
            record_id = cursor.fetchone()

            if record_id:
                cursor.execute("DELETE FROM righecolore WHERE colore_id = ?", (record_id[0],))
                cursor.execute("DELETE FROM colore WHERE id = ?", (record_id[0],))
                conn.commit()

            # Rimuove il record dalla tabella
            self.table.delete(selected_item[0])

            messagebox.showinfo("Successo", "Record eliminato con successo.")
        except sqlite3.Error as e:
            messagebox.showerror("Errore", f"Errore durante l'eliminazione: {e}")
        finally:
            conn.close()
    
    def load_categories(self):
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            cursor.execute("SELECT descrizione FROM categoria")
            categories = cursor.fetchall()
            self.cat_search['values'] = [""] + [cat[0] for cat in categories]
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Errore", f"Errore nel caricamento delle categorie: {e}")
            
    def reset_search(self):
        self.codice_search.delete(0, tk.END)
        self.desc_search.delete(0, tk.END)
        self.cat_search.set("")
        self.rif_search.delete(0, tk.END)
        self.populate_table()  # Ricarica tutti i record
        
    def search_records(self):
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            query = """
                SELECT colore.codice, colore.nome, categoria.descrizione, colore.riferimento
                FROM colore
                LEFT JOIN categoria ON colore.categoria_id = categoria.id
                WHERE 1=1
            """
            params = []
            
            if self.codice_search.get():
                query += " AND colore.codice LIKE ?"
                params.append(f"%{self.codice_search.get()}%")
                
            if self.desc_search.get():
                query += " AND colore.nome LIKE ?"
                params.append(f"%{self.desc_search.get()}%")
                
            if self.cat_search.get():
                query += " AND categoria.descrizione = ?"
                params.append(self.cat_search.get())
                
            if self.rif_search.get():
                query += " AND colore.riferimento LIKE ?"
                params.append(f"%{self.rif_search.get()}%")
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            # Aggiorna la tabella con i risultati
            for item in self.table.get_children():
                self.table.delete(item)
                
            for record in records:
                self.table.insert("", "end", values=record)
            
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Errore", f"Errore durante la ricerca: {e}")
            
    def populate_table(self):
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT colore.codice, colore.nome, categoria.descrizione, colore.riferimento
                FROM colore
                LEFT JOIN categoria ON colore.categoria_id = categoria.id;
            """)
            records = cursor.fetchall()
            for item in self.table.get_children():
                self.table.delete(item)
            
            for record in records:
                self.table.insert("", "end", values=record)
            
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Errore", f"Errore durante il caricamento dei dati: {e}")
    
    def show_details(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Attenzione", "Seleziona un record per visualizzare i dettagli.")
            return

        item_values = self.table.item(selected_item[0])["values"]
        codice = item_values[0]

        dialog = tk.Toplevel(self)
        dialog.title("Dettagli del Record")
        dialog.geometry("600x600")

        dialog_frame = ttk.Frame(dialog, padding=10)
        dialog_frame.pack(fill="both", expand=True)

        info_frame = ttk.LabelFrame(dialog_frame, text="Informazioni Generali", padding=10)
        info_frame.pack(fill="x", pady=5)

        labels = [
            ("Codice:", item_values[0]),
            ("Descrizione:", item_values[1]),
            ("Categoria:", item_values[2]),
            ("Riferimento:", item_values[3]),
            ("Totale Quantità:", self.calculate_total_quantity(codice)),
        ]

        for i, (label, value) in enumerate(labels):
            ttk.Label(info_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(info_frame, text=str(value)).grid(row=i, column=1, sticky="w", padx=5, pady=2)

        details_frame = ttk.LabelFrame(dialog_frame, text="Dettagli Ricetta", padding=10)
        details_frame.pack(fill="both", expand=True, pady=5)

        self.details_table = ttk.Treeview(details_frame, columns=("Base", "Qt Originale", "Qt Ricalcolata"), show="headings")

        for col in self.details_table["columns"]:
            self.details_table.heading(col, text=col)
            self.details_table.column(col, width=150)

        self.details_table.pack(fill="both", expand=True)

        self.populate_recipe_details(self.details_table, codice)

        calc_frame = ttk.LabelFrame(dialog_frame, text="Impostazioni di Calcolo", padding=10)
        calc_frame.pack(fill="x", pady=5)

        ttk.Label(calc_frame, text="Approssimazione:").pack(side="left", padx=5)
        approximation_var = tk.DoubleVar(value=0.1)
        approximation_menu = ttk.Combobox(calc_frame, textvariable=approximation_var, values=[1, 0.5, 0.1], state="readonly", width=10)
        approximation_menu.pack(side="left", padx=5)

        ttk.Label(calc_frame, text="Quantità Totale:").pack(side="left", padx=5)
        quantity_input = ttk.Entry(calc_frame, width=10)
        quantity_input.pack(side="left", padx=5)

        calc_button = ttk.Button(
            calc_frame,
            text="Calcola",
            command=lambda: self.calculate_proportions(self.details_table, quantity_input, self.calculate_total_quantity(codice), approximation_var.get())
        )
        calc_button.pack(side="left", padx=5)

        pdf_button = ttk.Button(
            calc_frame,
            text="Invia PDF",
            command=self.invia_pdf
        )
        pdf_button.pack(side="left", padx=5)

    def calculate_total_quantity(self, codice):
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(quantita) FROM righecolore WHERE colore_id = (SELECT id FROM colore WHERE codice = ?)", (codice,))
            total = cursor.fetchone()[0]
            conn.close()
            return total if total else 0
        except sqlite3.Error as e:
            messagebox.showerror("Errore", f"Errore durante il calcolo del totale: {e}")
            return 0

    def populate_recipe_details(self, table, codice):
        try:
            conn = sqlite3.connect('laboratorio.db')
            cursor = conn.cursor()
            cursor.execute("SELECT base, quantita FROM righecolore WHERE colore_id = (SELECT id FROM colore WHERE codice = ?)", (codice,))
            records = cursor.fetchall()

            for record in records:
                table.insert("", "end", values=(record[0], record[1], ""))

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Errore", f"Errore durante il caricamento dei dettagli: {e}")

    def calculate_proportions(self, table, quantity_input, total_quantity, approximation):
        try:
            desired_total = float(quantity_input.get())
            if total_quantity == 0:
                raise ValueError("Quantità totale originale è zero, impossibile calcolare le proporzioni.")
            
            for item in table.get_children():
                values = table.item(item)["values"]
                original_quantity = float(values[1])
                recalculated_quantity = round((original_quantity / total_quantity) * desired_total / approximation) * approximation
                table.item(item, values=(values[0], values[1], f"{recalculated_quantity:.2f}"))
        except ValueError:
            messagebox.showwarning("Errore", "Inserisci un valore numerico valido per la quantità totale desiderata.")

    def invia_pdf(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Attenzione", "Seleziona un record per generare il PDF.")
            return

        item_values = self.table.item(selected_item[0])["values"]
        codice = item_values[0]
        descrizione = item_values[1]
        categoria = item_values[2]

        try:
            # Recupera le coppie base-quantità dalla tabella dei dettagli
            coppie = []
            for child in self.details_table.get_children():
                values = self.details_table.item(child)["values"]
                base = values[0]
                quantita_ricalcolata = values[2] if values[2] else values[1]
                coppie.append((base, quantita_ricalcolata))

            # Chiama la funzione per generare il PDF
            fill_and_save_word(codice, descrizione, categoria, coppie)
            messagebox.showinfo("Successo", "PDF generato correttamente!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la generazione del PDF: {e}")

    def delete_record(self):
        selected_item = self.table
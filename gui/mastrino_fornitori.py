import tkinter as tk
from tkinter import ttk
import csv

class MastrinoFornitoriPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Titolo della pagina
        title = tk.Label(self, text="Mastrino Fornitori", font=("Helvetica", 16, "bold"))
        title.pack(pady=20)

        # Contenuto specifico della pagina
        self.create_content()

    def create_content(self):
        # Frame principale per il contenuto
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Bottone IMPORTA
        import_button = ttk.Button(content_frame, text="IMPORTA", command=self.import_data)
        import_button.pack(pady=10, anchor="w")

        # Tabella
        columns = ("Sel", "Soggetto", "Num. Doc.", "Data", "Importo")
        self.tree = ttk.Treeview(content_frame, columns=columns, show="headings")

        # Configurazione colonne
        self.tree.heading("Sel", text="Sel")
        self.tree.column("Sel", width=50, anchor="center")
        self.tree.heading("Soggetto", text="Soggetto")
        self.tree.column("Soggetto", width=200, anchor="w")
        self.tree.heading("Num. Doc.", text="Num. Doc.")
        self.tree.column("Num. Doc.", width=100, anchor="center")
        self.tree.heading("Data", text="Data")
        self.tree.column("Data", width=100, anchor="center")
        self.tree.heading("Importo", text="Importo")
        self.tree.column("Importo", width=100, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        # Posizionamento tabella e scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def import_data(self):
        # Azione per il bottone IMPORTA
        csv_path = 'dati_estratti.csv'  # Path al file CSV
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.tree.insert(
                        "", "end",
                        values=("[ ]", row['Denominazione'], row['Numero'], row['Data'], row['ImportoTotaleDocumento'])
                    )
            print("Dati importati con successo!")
        except FileNotFoundError:
            print(f"Errore: File '{csv_path}' non trovato.")
        except KeyError as e:
            print(f"Errore: Colonna mancante nel file CSV - {e}")
        except Exception as e:
            print(f"Errore durante l'importazione: {e}")

# Codice per eseguire la pagina
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Mastrino Fornitori")
    MastrinoFornitoriPage(root).pack(fill="both", expand=True)
    root.geometry("700x400")
    root.mainloop()

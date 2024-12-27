# pratica_page.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QScrollArea, QPushButton, QMessageBox, QDialog, 
                             QFormLayout, QLabel, QLineEdit, QHBoxLayout)
import sqlite3

def create_pratica_page(stacked_widget):
    page = QWidget()
    layout = QVBoxLayout(page)

    # Bottone per visualizzare i dettagli
    detail_button = QPushButton("Mostra Dettagli")
    layout.addWidget(detail_button)

    # Creazione della tabella con scrolling
    table = QTableWidget()
    table.setColumnCount(4)
    table.setHorizontalHeaderLabels(["Codice", "Descrizione", "Categoria", "Riferimento"])
    
    # Popolamento della tabella con i dati dal database
    populate_table(table)

    # Aggiungere la tabella con scrolling
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(table)
    layout.addWidget(scroll_area)
    
    # Collegare il bottone alla funzione per mostrare i dettagli
    detail_button.clicked.connect(lambda: show_details(table))
    
    stacked_widget.addWidget(page)

def populate_table(table):
    try:
        conn = sqlite3.connect('laboratorio.db')
        cursor = conn.cursor()
        
        # Query per ottenere i dati con descrizione della categoria
        cursor.execute("""
            SELECT colore.codice, colore.nome, categoria.descrizione, colore.riferimento
            FROM colore
            LEFT JOIN categoria ON colore.categoria_id = categoria.id;
        """)
        records = cursor.fetchall()

        # Imposta il numero di righe della tabella
        table.setRowCount(len(records))
        
        # Inserisce i dati nella tabella
        for row_index, row_data in enumerate(records):
            for col_index, data in enumerate(row_data):
                table.setItem(row_index, col_index, QTableWidgetItem(str(data)))
        
        conn.close()
    except sqlite3.Error as e:
        print(f"Errore durante il caricamento dei dati: {e}")

def show_details(table):
    selected_row = table.currentRow()
    if selected_row == -1:
        QMessageBox.warning(None, "Attenzione", "Seleziona un record per visualizzare i dettagli.")
        return

    codice = table.item(selected_row, 0).text()
    nome = table.item(selected_row, 1).text()
    categoria = table.item(selected_row, 2).text()
    riferimento = table.item(selected_row, 3).text()

    # Crea una finestra di dialogo per mostrare i dettagli della ricetta
    dialog = QDialog()
    dialog.setWindowTitle("Dettagli del Record")
    layout = QVBoxLayout(dialog)

    # Informazioni principali
    info_layout = QFormLayout()
    info_layout.addRow("Codice:", QLabel(codice))
    info_layout.addRow("Descrizione:", QLabel(nome))
    info_layout.addRow("Categoria:", QLabel(categoria))
    info_layout.addRow("Riferimento:", QLabel(riferimento))

    # Calcola e visualizza il totale delle quantità
    total_quantity = calculate_total_quantity(codice)
    info_layout.addRow("Totale Quantità:", QLabel(str(total_quantity)))
    
    layout.addLayout(info_layout)

    # Tabella per i dettagli della ricetta con colonna per quantità ricalcolata
    details_table = QTableWidget()
    details_table.setColumnCount(3)
    details_table.setHorizontalHeaderLabels(["Base", "Quantità", "Quantità Ricalcolata"])
    populate_recipe_details(details_table, codice)
    layout.addWidget(details_table)

    # Campo per calcolo proporzionale
    calc_layout = QHBoxLayout()
    calc_layout.addWidget(QLabel("Quantità totale desiderata:"))
    quantity_input = QLineEdit()
    calc_layout.addWidget(quantity_input)
    layout.addLayout(calc_layout)

    # Pulsante per calcolare le quantità proporzionali
    calculate_button = QPushButton("Calcola Quantità Proporzionali")
    layout.addWidget(calculate_button)
    calculate_button.clicked.connect(lambda: calculate_proportions(details_table, quantity_input, total_quantity))

    dialog.exec_()

def calculate_total_quantity(codice):
    try:
        conn = sqlite3.connect('laboratorio.db')
        cursor = conn.cursor()
        
        # Query per ottenere e sommare le quantità di ogni componente della ricetta
        cursor.execute("""
            SELECT SUM(quantita)
            FROM righecolore
            WHERE colore_id = (SELECT id FROM colore WHERE codice = ?);
        """, (codice,))
        total = cursor.fetchone()[0]
        conn.close()
        
        return total if total else 0
    except sqlite3.Error as e:
        print(f"Errore durante il calcolo del totale delle quantità: {e}")
        return 0

def populate_recipe_details(table, codice):
    try:
        conn = sqlite3.connect('laboratorio.db')
        cursor = conn.cursor()

        # Query per ottenere i dettagli della ricetta basata sul codice del colore
        cursor.execute("""
            SELECT base, quantita
            FROM righecolore
            WHERE colore_id = (SELECT id FROM colore WHERE codice = ?);
        """, (codice,))
        records = cursor.fetchall()

        table.setRowCount(len(records))
        for row_index, (base, quantita) in enumerate(records):
            table.setItem(row_index, 0, QTableWidgetItem(base))
            table.setItem(row_index, 1, QTableWidgetItem(str(quantita)))
            table.setItem(row_index, 2, QTableWidgetItem(""))  # Colonna per Quantità Ricalcolata

        conn.close()
    except sqlite3.Error as e:
        print(f"Errore durante il caricamento dei dettagli della ricetta: {e}")

def calculate_proportions(table, quantity_input, total_quantity):
    try:
        # Prova a convertire l'input in un numero decimale
        desired_total = float(quantity_input.text().replace(',', '.'))
        
        # Calcolo delle quantità proporzionali
        for row in range(table.rowCount()):
            original_quantity = float(table.item(row, 1).text())
            recalculated_quantity = (original_quantity / total_quantity) * desired_total
            table.setItem(row, 2, QTableWidgetItem(f"{recalculated_quantity:.2f}"))
    except ValueError:
        QMessageBox.warning(None, "Errore", "Inserisci un valore numerico valido per la quantità totale desiderata.")

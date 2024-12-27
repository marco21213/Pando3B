import sys
import os

# Aggiunge la directory principale al percorso di ricerca dei moduli
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from gui.main_window import MainWindow
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

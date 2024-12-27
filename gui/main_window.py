import tkinter as tk

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaccia Grafica - Pando3B")

        # Ottieni le dimensioni dello schermo
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Configura la finestra per coprire il 100% del desktop
        self.root.geometry(f"{screen_width}x{screen_height}")

        # Semplice etichetta di esempio
        label = tk.Label(root, text="Benvenuto in Pando3B!", font=("Arial", 24))
        label.pack(expand=True)

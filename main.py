import sys
import os
import sqlite3
import configparser
import hashlib
import time
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog

# Aggiunge la directory principale al percorso di ricerca dei moduli
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui'))

from gui.main_window import MainWindow

class AuthenticationSystem:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        self.db_path = self.config.get('Autenticazione', 'percorso_database')
        self.max_attempts = self.config.getint('Autenticazione', 'max_tentativi_login')
        self.lockout_duration = self.config.getint('Autenticazione', 'durata_lockout_minuti')
        self.log_enabled = self.config.getboolean('Autenticazione', 'log_login_attempts')
        
        self.failed_attempts = {}
        self.lockouts = {}
        
        self.init_database()

    def init_database(self):
        """Inizializza il database se necessario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crea la tabella per i log degli accessi se non esiste
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT
                )
            ''')
            
            # Crea la tabella per i lockout se non esiste
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lockouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    lockout_until DATETIME NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Errore Database", f"Errore nell'inizializzazione del database: {str(e)}")

    def hash_password(self, password):
        """Hash della password usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def is_locked_out(self, username):
        """Controlla se l'utente è bloccato"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT lockout_until FROM lockouts WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result:
                lockout_until = datetime.fromisoformat(result[0])
                if datetime.now() < lockout_until:
                    return True, lockout_until
                else:
                    # Rimuovi il lockout scaduto
                    cursor.execute('DELETE FROM lockouts WHERE username = ?', (username,))
                    conn.commit()
            
            conn.close()
            return False, None
            
        except Exception as e:
            print(f"Errore nel controllo lockout: {e}")
            return False, None

    def add_lockout(self, username):
        """Aggiunge un lockout per l'utente"""
        try:
            lockout_until = datetime.now() + timedelta(minutes=self.lockout_duration)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO lockouts (username, lockout_until)
                VALUES (?, ?)
            ''', (username, lockout_until.isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Errore nell'aggiunta lockout: {e}")

    def log_login_attempt(self, username, success, ip_address=None):
        """Registra il tentativo di login"""
        if not self.log_enabled:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO login_logs (username, success, ip_address)
                VALUES (?, ?, ?)
            ''', (username, 1 if success else 0, ip_address))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Errore nel logging: {e}")

    def get_ip_address(self):
        """Ottiene l'indirizzo IP dell'utente (semplificato)"""
        try:
            import socket
            return socket.gethostbyname(socket.gethostname())
        except:
            return "Unknown"

    def authenticate(self, username, password):
        """Autentica l'utente"""
        # Controlla se l'utente è bloccato
        is_locked, lockout_until = self.is_locked_out(username)
        if is_locked:
            remaining = lockout_until - datetime.now()
            minutes = int(remaining.total_seconds() / 60)
            return False, f"Account bloccato. Riprova tra {minutes} minuti."

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cerca l'utente nel database - MODIFICATO: password_hash invece di password
            cursor.execute('SELECT password_hash, attivo FROM utenti WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result:
                stored_hash, is_active = result
                
                # Controlla se l'utente è attivo
                if not is_active:
                    conn.close()
                    return False, "Account disabilitato. Contatta l'amministratore."
                
                input_hash = self.hash_password(password)
                
                if stored_hash == input_hash:
                    # Login riuscito
                    self.failed_attempts.pop(username, None)
                    self.log_login_attempt(username, True, self.get_ip_address())
                    conn.close()
                    return True, "Login riuscito!"
                else:
                    # Password errata
                    attempts = self.failed_attempts.get(username, 0) + 1
                    self.failed_attempts[username] = attempts
                    
                    if attempts >= self.max_attempts:
                        self.add_lockout(username)
                        self.failed_attempts.pop(username, None)
                        self.log_login_attempt(username, False, self.get_ip_address())
                        conn.close()
                        return False, f"Troppi tentativi falliti. Account bloccato per {self.lockout_duration} minuti."
                    
                    remaining_attempts = self.max_attempts - attempts
                    self.log_login_attempt(username, False, self.get_ip_address())
                    conn.close()
                    return False, f"Password errata. Tentativi rimanenti: {remaining_attempts}"
            else:
                # Utente non trovato
                self.log_login_attempt(username, False, self.get_ip_address())
                conn.close()
                return False, "Utente non trovato."
                
        except Exception as e:
            print(f"Errore durante l'autenticazione: {e}")
            return False, f"Errore di sistema: {str(e)}"

def show_login_window():
    """Mostra la finestra di login"""
    root = tk.Tk()
    root.title("Login - Contabilità 3b")
    root.geometry("400x400")  # Aumentata l'altezza per i nuovi pulsanti
    root.resizable(False, False)
    
    # Centra la finestra
    root.eval('tk::PlaceWindow . center')
    
    # Frame principale con scrollbar
    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill='both', padx=20, pady=20)
    
    # Titolo
    title_label = tk.Label(main_frame, text="Accesso al Sistema", font=("Arial", 16, "bold"))
    title_label.pack(pady=(10, 20))
    
    # Container per i campi di input
    input_frame = tk.Frame(main_frame)
    input_frame.pack(fill='x', pady=(0, 20))
    
    # Username
    username_frame = tk.Frame(input_frame)
    username_frame.pack(fill='x', pady=(0, 15))
    
    tk.Label(username_frame, text="Username:", font=("Arial", 10)).pack(anchor='w', pady=(0, 5))
    username_entry = tk.Entry(username_frame, font=("Arial", 10), width=30)
    username_entry.pack(fill='x', pady=(0, 5))
    username_entry.focus()
    
    # Password
    password_frame = tk.Frame(input_frame)
    password_frame.pack(fill='x', pady=(0, 15))
    
    tk.Label(password_frame, text="Password:", font=("Arial", 10)).pack(anchor='w', pady=(0, 5))
    password_entry = tk.Entry(password_frame, font=("Arial", 10), width=30, show="*")
    password_entry.pack(fill='x', pady=(0, 5))
    
    # Messaggio di stato
    status_label = tk.Label(main_frame, text="", fg="red", font=("Arial", 9), wraplength=350)
    status_label.pack(pady=(0, 15))
    
    def attempt_login():
        username = username_entry.get().strip()
        password = password_entry.get()
        
        if not username or not password:
            status_label.config(text="Inserisci username e password")
            return
        
        auth_system = AuthenticationSystem()
        success, message = auth_system.authenticate(username, password)
        
        if success:
            status_label.config(text=message, fg="green")
            login_btn.config(state='disabled')
            exit_btn.config(state='disabled')
            root.after(1500, lambda: complete_login(root))
        else:
            status_label.config(text=message, fg="red")
    
    def complete_login(root_window):
        root_window.destroy()
        start_main_application()
    
    def exit_application():
        if messagebox.askyesno("Conferma", "Sei sicuro di voler uscire?"):
            root.destroy()
    
    # Frame per i pulsanti
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill='x', pady=(10, 0))
    
    # Pulsante di login
    login_btn = tk.Button(button_frame, text="Accedi", command=attempt_login, 
                         bg="#007acc", fg="white", font=("Arial", 10, "bold"),
                         width=12, height=1)
    login_btn.pack(side='left', padx=(0, 10))
    
    # Pulsante Esci
    exit_btn = tk.Button(button_frame, text="Esci", command=exit_application,
                        bg="#dc3545", fg="white", font=("Arial", 10),
                        width=8, height=1)
    exit_btn.pack(side='right')
    
    # Pulsante Configurazione (solo per amministratori)
    def open_config():
        try:
            from gui.config_window import ConfigWindow
            config_win = ConfigWindow(root)
            config_win.window.wait_window()  # Attende la chiusura della finestra
        except ImportError as e:
            messagebox.showerror("Errore", "Impossibile aprire la configurazione")
    
    config_btn = tk.Button(button_frame, text="Configura", command=open_config,
                          bg="#6c757d", fg="white", font=("Arial", 10),
                          width=10, height=1)
    config_btn.pack(side='right', padx=(0, 10))
    
    # Bind Enter per il login
    root.bind('<Return>', lambda event: attempt_login())
    
    # Info versione
    version_label = tk.Label(main_frame, text="Contabilità 3B v1.0", 
                            font=("Arial", 8), fg="gray")
    version_label.pack(side='bottom', pady=(20, 0))
    
    root.mainloop()

def start_main_application():
    """Avvia l'applicazione principale dopo il login"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    show_login_window()
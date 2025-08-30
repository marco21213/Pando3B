import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connetti al database e aggiorna le password
conn = sqlite3.connect('C:\\Users\\user\\Desktop\\Pando3B\\db\\database.db')
cursor = conn.cursor()

cursor.execute('SELECT id, password FROM utenti')
users = cursor.fetchall()

for user_id, plain_password in users:
    hashed = hash_password(plain_password)
    cursor.execute('UPDATE utenti SET password = ? WHERE id = ?', (hashed, user_id))

conn.commit()
conn.close()
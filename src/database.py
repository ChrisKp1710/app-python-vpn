import sqlite3
import hashlib
from encryption import encrypt_data, decrypt_data  # ✅ Importiamo crittografia centralizzata

DB_NAME = "users.db"

def initialize_database():
    """Crea il database e la tabella utenti se non esistono."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash della password con SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Registra un nuovo utente e assegna il primo come admin."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    role = "admin" if count == 0 else "user"

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (username, hash_password(password), role))
        conn.commit()
        return encrypt_data("REGISTERED")  # ✅ Cripta la risposta
    except sqlite3.IntegrityError:
        return encrypt_data("USERNAME_EXISTS")  # ✅ Cripta la risposta
    finally:
        conn.close()

def login_user(username, password):
    """Verifica le credenziali di login."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    hashed_password = hash_password(password)
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", 
                   (username, hashed_password))
    user = cursor.fetchone()
    
    conn.close()

    if user:
        return encrypt_data("SUCCESS"), user[0]  # ✅ Cripta il messaggio di successo
    return encrypt_data("INVALID_CREDENTIALS"), None  # ✅ Cripta il messaggio di errore

import sqlite3
from hashlib import sha256

def criar_usuarios_iniciais():
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logins (
                login TEXT PRIMARY KEY,
                senha TEXT NOT NULL
            )
        """)
        # Substitua pelos logins e senhas desejados
        usuarios = [
            ("Gbrito", sha256("admin123".encode()).hexdigest()),
            ("Marcelo", sha256("Marcelo123".encode()).hexdigest()),
            ("Carla", sha256("Carla123".encode()).hexdigest())
        ]

        for user in usuarios:
            cursor.execute("INSERT OR IGNORE INTO logins (login, senha) VALUES (?, ?)", user)

        conn.commit()
    finally:
        conn.close()

criar_usuarios_iniciais()

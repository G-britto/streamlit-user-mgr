import sqlite3
from hashlib import sha256

def autenticar(cursor, login, senha):
    """
    Verifica se o login e senha estão corretos.
    """
    senha_hash = sha256(senha.encode()).hexdigest()
    cursor.execute("SELECT * FROM logins WHERE login = ? AND senha = ?", (login, senha_hash))
    return cursor.fetchone() is not None

def obter_usuarios(cursor):
    """
    Retorna todos os usuários da tabela 'usuarios'.
    """
    cursor.execute("SELECT * FROM usuarios")
    return cursor.fetchall()

def adicionar_usuario(cursor, grupo, nome, login, email):
    """
    Adiciona um novo usuário à tabela 'usuarios'.
    """
    cursor.execute("INSERT INTO usuarios (grupo, nome, login, email) VALUES (?, ?, ?, ?)", 
                   (grupo, nome, login, email))

def editar_usuario(cursor, login_antigo, grupo, nome, login, email):
    """
    Edita os dados de um usuário existente.
    """
    cursor.execute("""
        UPDATE usuarios
        SET grupo = ?, nome = ?, login = ?, email = ?
        WHERE login = ?
    """, (grupo, nome, login, email, login_antigo))

def excluir_usuario(cursor, login):
    """
    Remove um usuário da tabela 'usuarios'.
    """
    cursor.execute("DELETE FROM usuarios WHERE login = ?", (login,))

def registrar_acao(cursor, acao, grupo, nome, login, email):
    """
    Registra uma ação na tabela 'historico'.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO historico (acao, grupo, nome, login, email, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (acao, grupo, nome, login, email, timestamp))

def obter_historico(cursor):
    """
    Retorna o histórico de ações da tabela 'historico'.
    """
    cursor.execute("SELECT * FROM historico")
    return cursor.fetchall()

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

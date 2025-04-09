import sqlite3
import pandas as pd

# Conectar ao banco de dados
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Recriar a tabela para remover a restrição de unicidade em 'login'
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo TEXT,
    nome TEXT,
    login TEXT,
    email TEXT
)
""")

# Migrar dados da tabela antiga para a nova tabela (se existir)
cursor.execute("""
INSERT INTO usuarios_temp (grupo, nome, login, email)
SELECT grupo, nome, login, email FROM usuarios
""")

# Excluir a tabela antiga e renomear a nova tabela
cursor.execute("DROP TABLE IF EXISTS usuarios")
cursor.execute("ALTER TABLE usuarios_temp RENAME TO usuarios")

# Ler o CSV (atenção aos nomes exatos das colunas)
try:
    df = pd.read_csv("usuarios_dos_grupos.csv")
    if df.empty:
        print("⚠️ O arquivo CSV está vazio ou não foi lido corretamente.")
        conn.close()
        exit()
except Exception as e:
    print(f"⚠️ Erro ao ler o arquivo CSV: {e}")
    conn.close()
    exit()

# Verificar duplicatas no CSV (apenas para exibir um aviso, mas não impedir a inserção)
duplicados = df[df.duplicated(subset=["Login"], keep=False)]
if not duplicados.empty:
    print("⚠️ Duplicatas encontradas no CSV (serão inseridas no banco):")
    print(duplicados)

inseridos = 0
ignorados = []

for _, row in df.iterrows():
    grupo = str(row.get("Grupo", "")).strip()
    nome = str(row.get("Nome", "")).strip()
    login = str(row.get("Login", "")).strip()
    email = str(row.get("Email", "")).strip()

    if not all([grupo, nome, login, email]):
        ignorados.append((login or "(sem login)", "Campos vazios"))
        continue

    # Inserir no banco (permitindo duplicatas)
    cursor.execute("""
        INSERT INTO usuarios (grupo, nome, login, email)
        VALUES (?, ?, ?, ?)
    """, (grupo, nome, login, email))
    inseridos += 1

conn.commit()
conn.close()

# Relatório de inserção
print(f"✅ {inseridos} usuários inseridos com sucesso.")
if ignorados:
    print("\n⚠️ Usuários ignorados:")
    for login, motivo in ignorados:
        print(f" - {login} → {motivo}")

# Exibir resumo dos dados importados
print("Dados importados com sucesso.")
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM usuarios")
count = cursor.fetchone()[0]
conn.close()
print(f"{count} usuários estão no banco de dados.")


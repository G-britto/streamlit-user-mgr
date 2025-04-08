import sqlite3
import pandas as pd

# Conectando ao banco
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Criar tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    grupo TEXT,
    nome TEXT,
    login TEXT PRIMARY KEY,
    email TEXT
)
""")

# Lendo o CSV
df = pd.read_csv("usuarios_dos_grupos.csv")

# Renomeando colunas, se necessário
df.rename(columns={
    "Grupo": "grupo",
    "Nome": "nome",
    "Login": "login",
    "Email": "email"
}, inplace=True)

# Verificando se todas as colunas necessárias estão presentes
required_columns = {"grupo", "nome", "login", "email"}
if not required_columns.issubset(df.columns):
    raise ValueError(f"O arquivo CSV deve conter as colunas: {required_columns}")

# Inserindo os dados no banco
for _, row in df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (grupo, nome, login, email)
        VALUES (?, ?, ?, ?)
    """, (row["grupo"], row["nome"], row["login"], row["email"]))

conn.commit()
conn.close()

print("Dados importados com sucesso.")
# Aqui você pode adicionar o código para verificar se os dados foram importados corretamente, se necessário.
# Se você quiser, pode adicionar uma função para verificar os dados importados  e exibir um resumo.
# Por exemplo, você pode contar quantos usuários foram importados e exibir essa informação.     
# Isso pode ser feito com uma consulta SQL simples após a inserção dos dados.
#
# Exemplo de verificação:
conn = sqlite3.connect("database.db") 
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM usuarios")
count = cursor.fetchone()[0]
conn.close()
print(f"{count} usuários foram importados com sucesso.")


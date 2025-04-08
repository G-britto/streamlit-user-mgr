import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from utils import (
    autenticar, obter_usuarios,
    adicionar_usuario, editar_usuario, excluir_usuario,
    registrar_acao, obter_historico
)
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Gerenciador de Usuários", layout="wide")

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

def inicializar_banco(cursor):
    """
    Initializes the database with the required tables.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        grupo TEXT,
        nome TEXT,
        login TEXT PRIMARY KEY,
        email TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        acao TEXT,
        grupo TEXT,
        nome TEXT,
        login TEXT,
        email TEXT,
        timestamp TEXT
    )
    """)

inicializar_banco(cursor)

# --- LOGIN ---
st.title("🔐 Login")
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    login = st.text_input("Login")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if autenticar(cursor, login, senha):
            st.session_state.logado = True
            st.experimental_rerun()
        else:
            st.error("Login ou senha incorretos.")
    st.stop()

# --- APLICATIVO PRINCIPAL ---
st.title("👥 Gerenciador de Usuários")

usuarios = obter_usuarios(cursor)
grupos_disponiveis = sorted(list(set([u[0] for u in usuarios])))
grupo_selecionado = st.selectbox("📂 Filtrar por Grupo", ["Todos"] + grupos_disponiveis)

usuarios_filtrados = [u for u in usuarios if grupo_selecionado == "Todos" or u[0] == grupo_selecionado]

# --- ADICIONAR USUÁRIO ---
with st.form("form_add"):
    st.subheader("➕ Adicionar Usuário")
    col1, col2, col3, col4 = st.columns(4)
    grupo = col1.text_input("Grupo")
    nome = col2.text_input("Nome")
    login_u = col3.text_input("Login")
    email = col4.text_input("Email")
    submit = st.form_submit_button("Adicionar")
    if submit and grupo and nome and login_u and email:
        adicionar_usuario(cursor, grupo, nome, login_u, email)
        registrar_acao(cursor, "Adicionado", grupo, nome, login_u, email)
        conn.commit()
        st.success(f"Usuário {nome} adicionado!")
        st.experimental_rerun()

# --- LISTAR USUÁRIOS ---
st.subheader("📄 Lista de Usuários")
for idx, u in enumerate(usuarios_filtrados):
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        st.write(f"**{u[1]}** | {u[2]} | {u[3]} | Grupo: *{u[0]}*")
    with col2:
        if st.button("✏️ Editar", key=f"editar_{idx}"):
            with st.form(f"form_edit_{idx}"):
                col1, col2, col3, col4 = st.columns(4)
                novo_grupo = col1.text_input("Grupo", u[0])
                novo_nome = col2.text_input("Nome", u[1])
                novo_login = col3.text_input("Login", u[2])
                novo_email = col4.text_input("Email", u[3])
                salvar = st.form_submit_button("Salvar")
                if salvar:
                    editar_usuario(cursor, u[2], novo_grupo, novo_nome, novo_login, novo_email)
                    registrar_acao(cursor, "Editado", novo_grupo, novo_nome, novo_login, novo_email)
                    conn.commit()
                    st.success("Usuário editado com sucesso!")
                    st.experimental_rerun()
    with col3:
        if st.button("🗑️ Excluir", key=f"excluir_{idx}"):
            excluir_usuario(cursor, u[2])
            registrar_acao(cursor, "Excluído", u[0], u[1], u[2], u[3])
            conn.commit()
            st.success("Usuário excluído.")
            st.experimental_rerun()

# --- HISTÓRICO ---
st.subheader("🕓 Histórico de Ações")
historico = obter_historico(cursor)
df_hist = pd.DataFrame(historico, columns=["Ação", "Grupo", "Nome", "Login", "Email", "Timestamp"])
st.dataframe(df_hist.sort_values(by="Timestamp", ascending=False), use_container_width=True)

# --- GERAR RELATÓRIO PDF ---
st.subheader("📄 Gerar Relatório PDF")
if st.button("📥 Baixar Relatório em PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Usuários", ln=True, align="C")
    pdf.ln(10)
    for u in usuarios_filtrados:
        pdf.cell(200, 10, txt=f"Grupo: {u[0]} | Nome: {u[1]} | Login: {u[2]} | Email: {u[3]}", ln=True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    with open(temp_file.name, "rb") as f:
        st.download_button("📄 Baixar PDF", f, file_name="relatorio_usuarios.pdf")

conn.close()

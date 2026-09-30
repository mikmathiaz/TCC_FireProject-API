"""
Fire Watcher — Ponto de Entrada da Aplicação
"""

import sys
from pathlib import Path

# Inclusão da raiz do projeto no sys.path para garantir resolução consistente de pacotes
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

st.set_page_config(
    page_title="Fire Watcher - Login",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Tela de login em construção (aguardando especificações de design)
st.title("Fire Watcher")
st.subheader("Login em construção")
st.info("A interface de autenticação será implementada conforme as especificações.")

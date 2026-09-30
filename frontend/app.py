"""
Fire Watcher — Ponto de Entrada da Interface (Frontend MVC)
Trabalho de Conclusão de Curso (TCC II) — Bacharelado em Engenharia da Computação
"""

import sys
from pathlib import Path

# Inclusão da raiz do projeto no sys.path para garantir resolução consistente de pacotes
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from frontend.controllers.api_controller import api_controller
from frontend.components.header import render_header
from frontend.views.dashboard_view import render_dashboard_view
from frontend.views.detalhe_view import render_detalhe_view
from frontend.views.historico_view import render_historico_view
from frontend.views.configuracao_view import render_configuracao_view

# Configuração da página Streamlit (layout amplo, sem emojis no título)
st.set_page_config(
    page_title="Fire Watcher - Monitoramento de Queimadas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregamento de folha de estilos técnicos
css_path = ROOT_DIR / "frontend" / "assets" / "styles.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Verificação de status da API backend
status_backend = api_controller.check_health()
api_online = status_backend.get("online", False)
api_versao = status_backend.get("data", {}).get("versao", "1.0.0")

# Renderização do cabeçalho institucional
render_header(api_status=api_online, version=api_versao)

# Menu de navegação lateral (padrão MVC)
with st.sidebar:
    st.markdown("### Navegação do Sistema")
    opcao_menu = st.radio(
        label="Selecione o Módulo:",
        options=[
            "Dashboard Principal",
            "Detalhamento de Célula",
            "Histórico e Validação",
            "Configurações Operacionais"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("#### Informações do Sistema")
    st.caption(f"Status da API: {'Online' if api_online else 'Offline'}")
    st.caption("Resolução Espacial: 10m - 20m")
    st.caption("Satélite Principal: Sentinel-2 MSI")
    st.caption("Base de Validação: INPE BDQueimadas")

# Roteamento de Views conforme a opção selecionada
if opcao_menu == "Dashboard Principal":
    render_dashboard_view()
elif opcao_menu == "Detalhamento de Célula":
    render_detalhe_view()
elif opcao_menu == "Histórico e Validação":
    render_historico_view()
elif opcao_menu == "Configurações Operacionais":
    render_configuracao_view()

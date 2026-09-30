"""
Utilitários de Renderização de Interface para Streamlit — Fire Watcher
Garante renderização segura de HTML eliminando indentação e linhas em branco
que poderiam ser interpretadas erroneamente como blocos de código Markdown.
"""

import streamlit as st


def render_html(html_content: str):
    """
    Renderiza fragmentos HTML no Streamlit sem risco de interpretação
    como bloco de código Markdown. Remove espaços no início de cada linha
    e linhas vazias. Utiliza st.html se disponível, ou st.markdown como fallback.
    """
    if not html_content:
        return

    # Limpeza rigorosa: remove indentação de cada linha e ignora linhas vazias
    cleaned = "".join(line.strip() for line in html_content.strip().splitlines() if line.strip())

    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)

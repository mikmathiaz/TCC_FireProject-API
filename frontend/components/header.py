"""
Componente de Cabeçalho Técnico — Fire Watcher
Apresenta identificação institucional, título do projeto e status de conexão da API.
"""

import streamlit as st


def render_header(api_status: bool = False, version: str = "1.0.0"):
    """
    Renderiza o cabeçalho acadêmico e técnico da aplicação.
    """
    status_label = "Conectado" if api_status else "Desconectado"
    status_color = "#16a34a" if api_status else "#dc2626"
    status_bg = "#f0fdf4" if api_status else "#fef2f2"
    status_border = "#bbf7d0" if api_status else "#fecaca"

    header_html = f"""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1 class="header-title">Fire Watcher</h1>
                <div class="header-subtitle">
                    Sistema de Monitoramento Inteligente e Detecção Precoce de Queimadas
                </div>
                <div class="header-meta">
                    Trabalho de Conclusão de Curso (TCC II) | Engenharia da Computação | Versão {version}
                </div>
            </div>
            <div style="text-align: right;">
                <span style="
                    display: inline-block;
                    padding: 0.35rem 0.75rem;
                    font-size: 0.75rem;
                    font-weight: 600;
                    border-radius: 4px;
                    background: {status_bg};
                    color: {status_color};
                    border: 1px solid {status_border};
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">
                    API: {status_label}
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

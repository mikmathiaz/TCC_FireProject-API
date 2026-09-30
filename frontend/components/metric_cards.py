"""
Componente de Cartões Métricos Técnicos — Fire Watcher
Renderiza indicadores de monitoramento com formatação acadêmica precisa.
"""

import streamlit as st
from typing import Optional


def render_metric_card(
    label: str,
    value: str,
    description: Optional[str] = None,
    badge_text: Optional[str] = None,
    badge_type: Optional[str] = None
):
    """
    Renderiza um cartão métrico técnico.
    badge_type pode ser: 'critico', 'alto', 'moderado', 'baixo'.
    """
    badge_html = ""
    if badge_text and badge_type:
        badge_html = f'<span class="badge badge-{badge_type}">{badge_text}</span>'

    desc_html = f'<div class="metric-description">{description}</div>' if description else ""

    html = f"""
    <div class="metric-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="metric-label">{label}</div>
            {badge_html}
        </div>
        <div class="metric-value">{value}</div>
        {desc_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

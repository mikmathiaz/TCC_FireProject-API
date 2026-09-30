"""
Componente de Cartões Métricos Técnicos — Fire Watcher
Renderiza indicadores de monitoramento com formatação acadêmica precisa.
"""

from typing import Optional
from frontend.components.ui_utils import render_html


def render_metric_card(
    label: str,
    value: str,
    description: Optional[str] = None,
    badge_text: Optional[str] = None,
    badge_type: Optional[str] = None
):
    """
    Renderiza um cartão métrico técnico sem blocos de código Markdown.
    """
    badge_html = f'<span class="badge badge-{badge_type}">{badge_text}</span>' if (badge_text and badge_type) else ""
    desc_html = f'<div class="metric-description">{description}</div>' if description else ""

    html = (
        f'<div class="metric-box">'
        f'<div style="display: flex; justify-content: space-between; align-items: center;">'
        f'<div class="metric-label">{label}</div>'
        f'{badge_html}'
        f'</div>'
        f'<div class="metric-value">{value}</div>'
        f'{desc_html}'
        f'</div>'
    )
    render_html(html)

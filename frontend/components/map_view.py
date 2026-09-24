"""
Componente de Mapa Interativo — Folium & Streamlit-Folium
Renderiza a área de interesse, as camadas de risco dos 4 índices espectrais
e a camada de validação cruzada com focos de calor do INPE.
"""

import folium
from typing import List, Dict, Any, Optional

CORES_RISCO = {
    "Crítico": "#D32F2F",   # Vermelho escuro
    "Alto": "#F57C00",      # Laranja forte
    "Moderado": "#FBC02D",  # Amarelo âmbar
    "Baixo": "#2E7D32"      # Verde floresta
}


def criar_mapa_monitoramento(
    aoi: Dict[str, Any],
    celulas: List[Dict[str, Any]] = [],
    focos_inpe: List[Dict[str, Any]] = [],
    exibir_focos_inpe: bool = True
) -> folium.Map:
    """
    Constrói um mapa Folium centrado na AOI com as camadas de células de risco
    e focos históricos do INPE.
    """
    centro_lat = (aoi.get("min_lat", -15.65) + aoi.get("max_lat", -15.65)) / 2.0
    centro_lon = (aoi.get("min_lon", -47.95) + aoi.get("max_lon", -47.95)) / 2.0

    # Criação do mapa base
    m = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=11,
        tiles="CartoDB positron",
        control_scale=True
    )

    # Camada 1: Limites da Área de Interesse (Bounding Box)
    bounds = [
        [aoi.get("min_lat", -15.75), aoi.get("min_lon", -48.05)],
        [aoi.get("max_lat", -15.55), aoi.get("max_lon", -47.85)]
    ]
    folium.Rectangle(
        bounds=bounds,
        color="#1565C0",
        weight=2,
        fill=True,
        fill_color="#1E88E5",
        fill_opacity=0.08,
        popup=f"<b>AOI:</b> {aoi.get('nome', 'Área de Monitoramento')}",
        tooltip="Limite da Área de Interesse (Sentinel-2 AOI)"
    ).add_to(m)

    # Camada 2: Células de Índices Espectrais e Nível de Risco
    grupo_risco = folium.FeatureGroup(name="Grade de Risco (Sentinel-2)", show=True)
    for c in celulas:
        nivel = c.get("nivel_risco", "Baixo")
        cor = CORES_RISCO.get(nivel, "#2E7D32")
        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px; width: 200px;">
            <b style="color: {cor}; font-size: 14px;">Risco: {nivel}</b><br>
            <b>Pontuação:</b> {c.get('pontuacao_risco', 0):.1f}/100<br>
            <hr style="margin: 4px 0;">
            <b>NDVI (Vigor):</b> {c.get('ndvi', 0):.3f}<br>
            <b>NBR (Seca/Queima):</b> {c.get('nbr', 0):.3f}<br>
            <b>NDII (Água na Copa):</b> {c.get('ndii', 0):.3f}<br>
            <b>PSRI (Senescência):</b> {c.get('psri', 0):.3f}<br>
            <hr style="margin: 4px 0;">
            <small><i>{c.get('justificativa', '')}</i></small>
        </div>
        """

        folium.CircleMarker(
            location=[c["latitude"], c["longitude"]],
            radius=12,
            color=cor,
            weight=1.5,
            fill=True,
            fill_color=cor,
            fill_opacity=0.65,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"Risco {nivel} ({c.get('pontuacao_risco', 0):.1f})"
        ).add_to(grupo_risco)

    grupo_risco.add_to(m)

    # Camada 3: Focos de Calor Reais (INPE Queimadas)
    if exibir_focos_inpe and focos_inpe:
        grupo_inpe = folium.FeatureGroup(name="Focos Reais INPE (BDQueimadas)", show=True)
        for f in focos_inpe:
            popup_inpe = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b style="color: #b71c1c;">🔥 Foco de Calor INPE</b><br>
                <b>Satélite:</b> {f.get('satelite')}<br>
                <b>Data/Hora:</b> {str(f.get('data_hora'))[:19]}<br>
                <b>Dias sem Chuva:</b> {f.get('dias_sem_chuva', 'N/D')}<br>
                <b>FRP:</b> {f.get('frp', 'N/D')} MW<br>
                <b>Risco Fogo INPE:</b> {f.get('risco_fogo_inpe', 'N/D')}
            </div>
            """
            folium.CircleMarker(
                location=[f["latitude"], f["longitude"]],
                radius=7,
                color="#000000",
                weight=2,
                fill=True,
                fill_color="#FF1744",
                fill_opacity=0.9,
                popup=folium.Popup(popup_inpe, max_width=220),
                tooltip=f"Foco INPE: {f.get('satelite')}"
            ).add_to(grupo_inpe)
        grupo_inpe.add_to(m)

    folium.LayerControl().add_to(m)
    return m

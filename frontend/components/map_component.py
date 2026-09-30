"""
Componente de Mapa Geoespacial — Folium
Renderiza camadas vetoriais e matriciais do Sentinel-2 e validação INPE.
"""

import folium
from typing import List, Dict, Any

CORES_RISCO = {
    "Crítico": "#dc2626",
    "Alto": "#ea580c",
    "Moderado": "#ca8a04",
    "Baixo": "#16a34a"
}


def render_map(
    aoi: Dict[str, Any],
    celulas: List[Dict[str, Any]] = [],
    focos_inpe: List[Dict[str, Any]] = [],
    exibir_inpe: bool = True
) -> folium.Map:
    """
    Constrói a instância do mapa Folium com camadas de satélite e dados de referência.
    """
    centro_lat = (aoi.get("min_lat", -15.65) + aoi.get("max_lat", -15.65)) / 2.0
    centro_lon = (aoi.get("min_lon", -47.95) + aoi.get("max_lon", -47.95)) / 2.0

    m = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=11,
        tiles=None,
        control_scale=True
    )

    # Camadas base sem chave de API com atribuição oficial
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
        name="Satélite (Esri World Imagery)",
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Mapa Base (OpenStreetMap)",
        overlay=False,
        control=True
    ).add_to(m)

    # Limite da Área de Interesse (Bounding Box)
    bounds = [
        [aoi.get("min_lat", -15.75), aoi.get("min_lon", -48.05)],
        [aoi.get("max_lat", -15.55), aoi.get("max_lon", -47.85)]
    ]
    folium.Rectangle(
        bounds=bounds,
        color="#0284c7",
        weight=2,
        fill=True,
        fill_color="#38bdf8",
        fill_opacity=0.06,
        popup=f"AOI: {aoi.get('nome', 'Área de Monitoramento')}",
        tooltip="Limite Geográfico da AOI"
    ).add_to(m)

    # Camada de Zonas de Risco (Sentinel-2)
    grupo_risco = folium.FeatureGroup(name="Grade de Risco (Sentinel-2 MSI)", show=True)
    for c in celulas:
        nivel = c.get("nivel_risco", "Baixo")
        cor = CORES_RISCO.get(nivel, "#16a34a")
        
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; font-size: 11px; line-height: 1.4; min-width: 180px;">
            <div style="font-weight: 700; color: {cor}; font-size: 12px; margin-bottom: 4px;">
                NÍVEL: {nivel.upper()} ({c.get('pontuacao_risco', 0):.1f}/100)
            </div>
            <div style="border-top: 1px solid #cbd5e1; padding-top: 4px;">
                <b>NDVI:</b> {c.get('ndvi', 0):.3f}<br>
                <b>NBR:</b> {c.get('nbr', 0):.3f}<br>
                <b>NDII:</b> {c.get('ndii', 0):.3f}<br>
                <b>PSRI:</b> {c.get('psri', 0):.3f}
            </div>
            <div style="margin-top: 4px; font-size: 10px; color: #64748b;">
                Lat: {c['latitude']:.4f} | Lon: {c['longitude']:.4f}
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[c["latitude"], c["longitude"]],
            radius=11,
            color=cor,
            weight=1.5,
            fill=True,
            fill_color=cor,
            fill_opacity=0.6,
            popup=folium.Popup(popup_content, max_width=240),
            tooltip=f"Risco {nivel} ({c.get('pontuacao_risco', 0):.1f})"
        ).add_to(grupo_risco)

    grupo_risco.add_to(m)

    # Camada de Focos de Calor do INPE (Ground Truth)
    if exibir_inpe and focos_inpe:
        grupo_inpe = folium.FeatureGroup(name="Focos Oficiais INPE (BDQueimadas)", show=True)
        for f in focos_inpe:
            popup_inpe = f"""
            <div style="font-family: Arial, sans-serif; font-size: 11px; line-height: 1.4;">
                <div style="font-weight: 700; color: #991b1b; margin-bottom: 4px;">
                    FOCO DE CALOR INPE
                </div>
                <b>Satélite:</b> {f.get('satelite')}<br>
                <b>Data/Hora:</b> {str(f.get('data_hora'))[:19]}<br>
                <b>Dias sem Chuva:</b> {f.get('dias_sem_chuva', 'N/D')}<br>
                <b>FRP:</b> {f.get('frp', 'N/D')} MW<br>
                <b>Risco Fogo:</b> {f.get('risco_fogo_inpe', 'N/D')}
            </div>
            """
            folium.CircleMarker(
                location=[f["latitude"], f["longitude"]],
                radius=6,
                color="#450a0a",
                weight=1.5,
                fill=True,
                fill_color="#ef4444",
                fill_opacity=0.9,
                popup=folium.Popup(popup_inpe, max_width=220),
                tooltip=f"Foco INPE: {f.get('satelite')}"
            ).add_to(grupo_inpe)

        grupo_inpe.add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    return m

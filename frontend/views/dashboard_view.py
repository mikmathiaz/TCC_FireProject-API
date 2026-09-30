"""
View: Dashboard Principal — Fire Watcher
Apresenta o mapa geoespacial da AOI, camadas de risco espectral e focos do INPE.
"""

import streamlit as st
from streamlit_folium import st_folium
from frontend.components.ui_utils import render_html
from frontend.controllers.api_controller import api_controller
from frontend.components.metric_cards import render_metric_card
from frontend.components.map_component import render_map
from frontend.components.charts import plot_risk_distribution, plot_indices_dispersion


def render_dashboard_view():
    """
    Renderiza a interface do Dashboard Principal.
    """
    render_html('<div class="section-title">Painel de Monitoramento Geoespacial</div>')

    # Consulta de Áreas de Interesse
    aois = api_controller.get_aois()
    if not aois:
        st.warning("Nenhuma Área de Interesse cadastrada no sistema. Acesse a aba 'Configurações' para inicializar.")
        return

    col_filtro1, col_filtro2 = st.columns([1, 2])
    with col_filtro1:
        mapa_aois = {a["nome"]: a for a in aois}
        nome_selecionado = st.selectbox("Área de Interesse (AOI):", list(mapa_aois.keys()))
        aoi = mapa_aois[nome_selecionado]

    # Consulta de Análises Realizadas para esta AOI
    historico = [h for h in api_controller.get_analysis_history() if h["area_id"] == aoi["id"]]

    analise_selecionada = None
    with col_filtro2:
        if historico:
            mapa_analises = {
                f"Análise #{h['id']} | Data: {h['data_referencia'][:10]} | Risco Geral: {h['classificacao_geral']}": h['id']
                for h in historico
            }
            analise_label = st.selectbox("Cena de Satélite / Data de Referência:", list(mapa_analises.keys()))
            analise_id = mapa_analises[analise_label]
            analise_selecionada = api_controller.get_analysis_details(analise_id)
        else:
            st.info("Nenhuma análise processada ainda para esta AOI. Utilize a aba 'Configurações' para processar.")

    # Dados Meteorológicos da Região Central da AOI
    centro_lat = (aoi["min_lat"] + aoi["max_lat"]) / 2.0
    centro_lon = (aoi["min_lon"] + aoi["max_lon"]) / 2.0
    clima = api_controller.get_weather(centro_lat, centro_lon)

    # Cartões de Indicadores Técnicos
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        nivel = analise_selecionada["classificacao_geral"] if analise_selecionada else "N/A"
        badge_map = {
            "Crítico": ("Crítico", "critico"),
            "Alto": ("Alto", "alto"),
            "Moderado": ("Moderado", "moderado"),
            "Baixo": ("Baixo", "baixo")
        }
        badge_t, badge_c = badge_map.get(nivel, ("N/A", "baixo"))
        render_metric_card(
            label="Nível Geral de Risco",
            value=nivel,
            description="Classificação integrada ponderada",
            badge_text=badge_t if analise_selecionada else None,
            badge_type=badge_c if analise_selecionada else None
        )

    with m2:
        score = analise_selecionada["pontuacao_risco_media"] if analise_selecionada else 0.0
        render_metric_card(
            label="Pontuação de Inflamabilidade",
            value=f"{score:.1f} / 100",
            description="Média das células orbitais"
        )

    with m3:
        alerta = analise_selecionada["celulas_alto_risco"] if analise_selecionada else 0
        total = analise_selecionada["total_celulas"] if analise_selecionada else 0
        render_metric_card(
            label="Células em Estado de Alerta",
            value=f"{alerta} de {total}",
            description="Zonas classificadas como Alto ou Crítico"
        )

    with m4:
        temp = clima.get("temperatura_atual", 0.0)
        umid = clima.get("umidade_relativa_atual", 0.0)
        render_metric_card(
            label="Condição Meteorológica Local",
            value=f"{temp:.1f} °C | {umid:.0f}% UR",
            description="Estação meteorológica Open-Meteo"
        )

    render_html("<br>")

    # Painel Principal com Mapa e Gráficos
    col_mapa, col_graficos = st.columns([3, 2])

    with col_graficos:
        render_html('<div class="section-title">Estatísticas da Área</div>')
        exibir_inpe = st.checkbox("Exibir Camada de Focos INPE (Ground Truth)", value=True)
        
        celulas = analise_selecionada.get("indices", []) if analise_selecionada else []
        if celulas:
            st.plotly_chart(plot_risk_distribution(celulas), use_container_width=True)
            st.plotly_chart(plot_indices_dispersion(celulas), use_container_width=True)
        else:
            st.info("Execute uma análise para visualizar a distribuição dos índices.")

    with col_mapa:
        render_html('<div class="section-title">Distribuição Espacial de Risco (Sentinel-2)</div>')
        focos_inpe = api_controller.get_inpe_focos(limit=100) if exibir_inpe else []

        mapa = render_map(
            aoi=aoi,
            celulas=celulas,
            focos_inpe=focos_inpe,
            exibir_inpe=exibir_inpe
        )
        st_folium(mapa, width="100%", height=590)

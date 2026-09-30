"""
View: Detalhamento de Área — Fire Watcher
Apresenta a inspeção individualizada das células geográficas e dos 4 índices espectrais.
"""

import streamlit as st
from frontend.controllers.api_controller import api_controller
from frontend.components.metric_cards import render_metric_card
from frontend.components.charts import plot_radar_profile


def render_detalhe_view():
    """
    Renderiza a interface de detalhamento por célula geográfica.
    """
    st.markdown('<div class="section-title">Detalhamento e Análise Biofísica por Célula</div>', unsafe_allow_html=True)

    historico = api_controller.get_analysis_history()
    if not historico:
        st.warning("Nenhuma análise disponível. Execute uma análise na aba 'Configurações' primeiro.")
        return

    mapa_analises = {
        f"Análise #{h['id']} | Data: {h['data_referencia'][:10]} | Sensor: {h['satelite']}": h['id']
        for h in historico
    }
    analise_label = st.selectbox("Selecione a Análise a Detalhar:", list(mapa_analises.keys()))
    analise = api_controller.get_analysis_details(mapa_analises[analise_label])

    if not analise or not analise.get("indices"):
        st.warning("Não há células processadas nesta análise.")
        return

    celulas = analise["indices"]

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        filtro_risco = st.selectbox("Filtrar Células por Severidade:", ["Todos", "Crítico", "Alto", "Moderado", "Baixo"])

    celulas_filtradas = (
        celulas if filtro_risco == "Todos"
        else [c for c in celulas if c["nivel_risco"] == filtro_risco]
    )

    if not celulas_filtradas:
        st.info("Nenhuma célula encontrada com o filtro selecionado.")
        return

    with col_f2:
        mapa_celulas = {
            f"Lat: {c['latitude']:.4f}, Lon: {c['longitude']:.4f} | Risco: {c['nivel_risco']} ({c['pontuacao_risco']:.1f}/100)": c
            for c in celulas_filtradas
        }
        celula_label = st.selectbox("Selecione a Coordenada da Célula:", list(mapa_celulas.keys()))
        celula = mapa_celulas[celula_label]

    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)

    col_resumo, col_radar = st.columns([3, 2])

    with col_resumo:
        st.markdown(f"#### Coordenada: Latitude `{celula['latitude']}`, Longitude `{celula['longitude']}`")
        
        # Diagnóstico técnico
        st.info(f"**Diagnóstico Técnico:** {celula.get('justificativa', 'Sem diagnóstico registrado.')}")

        c1, c2 = st.columns(2)
        with c1:
            render_metric_card(
                label="NDVI (Vigor Vegetativo)",
                value=f"{celula['ndvi']:.3f}",
                description="Fórmula: (B8 - B4) / (B8 + B4)"
            )
            st.markdown("<br>", unsafe_allow_html=True)
            render_metric_card(
                label="NDII (Água na Copa Foliar)",
                value=f"{celula['ndii']:.3f}",
                description="Fórmula: (B8 - B11) / (B8 + B11)"
            )

        with c2:
            render_metric_card(
                label="NBR (Razão Normalizada de Queima)",
                value=f"{celula['nbr']:.3f}",
                description="Fórmula: (B8 - B12) / (B8 + B12)"
            )
            st.markdown("<br>", unsafe_allow_html=True)
            render_metric_card(
                label="PSRI (Senescência da Biomassa)",
                value=f"{celula['psri']:.3f}",
                description="Fórmula: (B4 - B2) / B8"
            )

    with col_radar:
        st.plotly_chart(plot_radar_profile(celula), use_container_width=True)

    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # Metadados da Cena de Satélite
    st.markdown("#### Metadados da Cena Orbital")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.caption("Plataforma Orbital")
        st.code(analise.get("satelite", "Sentinel-2 MSI"))
    with m_col2:
        st.caption("Identificador da Cena")
        st.code(analise.get("id_cena_satelite", "S2_MSI_L2A"))
    with m_col3:
        st.caption("Data de Passagem")
        st.code(analise.get("data_referencia", "")[:10])
    with m_col4:
        st.caption("Resolução Espacial")
        st.code("10m (B2, B4, B8) | 20m (B11, B12)")

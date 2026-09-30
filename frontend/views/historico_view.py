"""
View: Painel de Histórico e Alertas — Fire Watcher
Apresenta o histórico cronológico de análises e o módulo de validação cruzada contra o INPE.
"""

import streamlit as st
import pandas as pd
from frontend.components.ui_utils import render_html
from frontend.controllers.api_controller import api_controller
from frontend.components.metric_cards import render_metric_card


def render_historico_view():
    """
    Renderiza a interface do painel de histórico e validação cruzada.
    """
    render_html('<div class="section-title">Histórico de Análises e Validação Cruzada (BDQueimadas/INPE)</div>')

    historico = api_controller.get_analysis_history()
    if not historico:
        st.info("Nenhuma análise processada até o momento. Acesse a aba 'Configurações' para iniciar um processamento.")
        return

    # Tabela Cronológica de Análises
    st.markdown("#### Registro Cronológico de Processamentos")
    df_h = pd.DataFrame(historico)
    df_show = df_h[[
        "id", "data_referencia", "satelite", "classificacao_geral",
        "pontuacao_risco_media", "total_celulas", "celulas_alto_risco", "processada_em"
    ]].copy()
    df_show["data_referencia"] = df_show["data_referencia"].str[:10]
    df_show["processada_em"] = df_show["processada_em"].str[:19]
    df_show.columns = [
        "ID", "Data da Imagem", "Sensor Orbital", "Risco Geral",
        "Score Médio", "Total Células", "Células em Alerta", "Processado em"
    ]
    st.dataframe(df_show, use_container_width=True)

    st.divider()

    # Módulo de Validação Cruzada
    st.markdown("#### Módulo de Validação Cruzada contra Focos do INPE")
    st.caption("Confronta as zonas previstas como Alto/Crítico risco contra os focos térmicos reais reportados pelo BDQueimadas.")

    c_v1, c_v2 = st.columns([2, 1])
    with c_v1:
        mapa_analises = {
            f"Análise #{h['id']} | Data: {h['data_referencia'][:10]} | Risco Geral: {h['classificacao_geral']}": h['id']
            for h in historico
        }
        analise_label = st.selectbox("Selecione a análise para confronto:", list(mapa_analises.keys()))
        id_selecionado = mapa_analises[analise_label]

    with c_v2:
        raio_tolerancia = st.slider(
            "Raio de Tolerância Espacial (metros):",
            min_value=200,
            max_value=3000,
            value=1000,
            step=100,
            help="Distância euclidiana/geodésica máxima admitida entre o foco INPE e uma célula de risco do Sentinel-2."
        )

    if st.button("Executar Validação Cruzada", type="primary"):
        with st.spinner("Calculando correspondência espacial com a base do INPE..."):
            res = api_controller.run_cross_validation(id_selecionado, tolerance_m=float(raio_tolerancia))
            if res:
                st.success("Validação cruzada executada com sucesso.")
            else:
                st.error("Não foi possível executar a validação. Verifique se existem focos do INPE cadastrados na base.")

    # Relatórios de Validação Salvos
    validacoes = api_controller.get_validation_history()
    if validacoes:
        render_html("<br>")
        st.markdown("#### Relatórios de Validação Registrados")
        
        ultima = validacoes[0]
        m1, m2, m3 = st.columns(3)
        with m1:
            render_metric_card(
                label="Taxa de Coincidência (Acerto)",
                value=f"{ultima['taxa_coincidencia_percentual']:.1f}%",
                description="Focos coincidentes sobre o total detectado"
            )
        with m2:
            render_metric_card(
                label="Focos em Zona de Risco",
                value=f"{ultima['focos_em_zona_alto_risco']} de {ultima['total_focos_inpe_detectados']}",
                description="Interseção espacial dentro do raio de tolerância"
            )
        with m3:
            dist = ultima.get('distancia_media_foco_zona_metros', 0)
            render_metric_card(
                label="Distância Média ao Risco",
                value=f"{dist:.0f} metros",
                description="Distância média foco-célula de risco"
            )

        df_v = pd.DataFrame(validacoes)
        df_v_show = df_v[[
            "id", "analise_id", "total_focos_inpe_detectados",
            "focos_em_zona_alto_risco", "taxa_coincidencia_percentual",
            "distancia_media_foco_zona_metros", "executada_em"
        ]].copy()
        df_v_show["executada_em"] = df_v_show["executada_em"].str[:19]
        df_v_show.columns = [
            "ID Validação", "ID Análise", "Total Focos INPE",
            "Focos Coincidentes", "Taxa Acerto (%)", "Distância Média (m)", "Executada em"
        ]
        st.dataframe(df_v_show, use_container_width=True)

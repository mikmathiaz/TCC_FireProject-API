"""
Tela 1: Dashboard Principal — Mapa Interativo de Risco de Queimadas
"""

import streamlit as st
from streamlit_folium import st_folium
from frontend.services.api_client import api_client
from frontend.components.map_view import criar_mapa_monitoramento
from frontend.components.charts import plot_distribuicao_risco, plot_histograma_indices

st.set_page_config(page_title="Dashboard Principal — Fire Watcher", page_icon="🗺️", layout="wide")

st.title("🗺️ Dashboard Principal de Monitoramento")

# Seleção de AOI e Análise
aois = api_client.get_aois()
if not aois:
    st.warning("Nenhuma Área de Interesse cadastrada. Vá até 'Configurações' para inicializar.")
    st.stop()

col_sel1, col_sel2 = st.columns([1, 2])
with col_sel1:
    aoi_nomes = {a["nome"]: a for a in aois}
    aoi_escolhida_nome = st.selectbox("Área de Interesse (AOI):", list(aoi_nomes.keys()))
    aoi = aoi_nomes[aoi_escolhida_nome]

# Busca histórico para esta AOI
historico = [h for h in api_client.get_analysis_history() if h["area_id"] == aoi["id"]]

analise_selecionada = None
with col_sel2:
    if historico:
        opcoes_analise = {
            f"Análise #{h['id']} — {h['data_referencia'][:10]} (Risco Geral: {h['classificacao_geral']})": h['id']
            for h in historico
        }
        analise_key = st.selectbox("Data da Imagem / Análise:", list(opcoes_analise.keys()))
        analise_id = opcoes_analise[analise_key]
        analise_selecionada = api_client.get_analysis_details(analise_id)
    else:
        st.info("Nenhuma análise processada ainda para esta AOI. Você pode processar uma em 'Configurações'.")

# Dados meteorológicos atuais para a AOI
centro_lat = (aoi["min_lat"] + aoi["max_lat"]) / 2.0
centro_lon = (aoi["min_lon"] + aoi["max_lon"]) / 2.0
clima = api_client.get_current_weather(centro_lat, centro_lon)

# Cartões de Métricas no Topo
m1, m2, m3, m4 = st.columns(4)
with m1:
    classificacao = analise_selecionada["classificacao_geral"] if analise_selecionada else "N/A"
    cor_map = {"Crítico": "🔴", "Alto": "🟠", "Moderado": "🟡", "Baixo": "🟢"}
    st.metric(
        label="Nível de Risco Geral",
        value=f"{cor_map.get(classificacao, '⚪')} {classificacao}"
    )

with m2:
    pontuacao = analise_selecionada["pontuacao_risco_media"] if analise_selecionada else 0.0
    st.metric(label="Pontuação Média de Risco", value=f"{pontuacao:.1f} / 100")

with m3:
    celulas_alerta = analise_selecionada["celulas_alto_risco"] if analise_selecionada else 0
    total = analise_selecionada["total_celulas"] if analise_selecionada else 0
    st.metric(label="Células em Alerta (Alto/Crítico)", value=f"{celulas_alerta} de {total}")

with m4:
    temp = clima.get("temperatura_atual", 0.0)
    umid = clima.get("umidade_relativa_atual", 0.0)
    st.metric(label="Clima Atual (Open-Meteo)", value=f"{temp}°C | {umid}% UR")

st.divider()

# Controles de Camadas do Mapa
col_mapa, col_stats = st.columns([3, 2])

with col_stats:
    st.markdown("#### Painel de Camadas e Estatísticas")
    exibir_inpe = st.checkbox("Exibir Focos do INPE (Ground Truth)", value=True)
    
    celulas = analise_selecionada.get("indices", []) if analise_selecionada else []
    
    if celulas:
        st.plotly_chart(plot_distribuicao_risco(celulas), use_container_width=True)
        st.plotly_chart(plot_histograma_indices(celulas), use_container_width=True)
    else:
        st.info("Execute uma análise para visualizar a distribuição dos índices.")

with col_mapa:
    st.markdown("#### Mapa Espacial de Risco (Sentinel-2)")
    focos_inpe = api_client.get_inpe_focos(limit=100) if exibir_inpe else []

    mapa = criar_mapa_monitoramento(
        aoi=aoi,
        celulas=celulas,
        focos_inpe=focos_inpe,
        exibir_focos_inpe=exibir_inpe
    )
    st_folium(mapa, width="100%", height=620)

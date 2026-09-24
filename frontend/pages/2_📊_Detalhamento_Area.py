"""
Tela 2: Detalhamento de Área Selecionada — Inspeção Minuciosa dos 4 Índices Espectrais
"""

import streamlit as st
import pandas as pd
from frontend.services.api_client import api_client
from frontend.components.charts import plot_radar_indices

st.set_page_config(page_title="Detalhamento de Área — Fire Watcher", page_icon="📊", layout="wide")

st.title("📊 Detalhamento de Área e Índices Espectrais")

# Seleção de Análise
historico = api_client.get_analysis_history()
if not historico:
    st.warning("Nenhuma análise encontrada. Processe uma análise na aba 'Configurações' primeiro.")
    st.stop()

opcoes_analise = {
    f"Análise #{h['id']} — {h['data_referencia'][:10]} ({h['satelite']})": h['id']
    for h in historico
}
analise_id = st.selectbox("Selecione a Análise a Detalhar:", list(opcoes_analise.keys()))
analise = api_client.get_analysis_details(opcoes_analise[analise_id])

if not analise or not analise.get("indices"):
    st.warning("Não há células processadas nesta análise.")
    st.stop()

celulas = analise["indices"]

# Seleção da célula por coordenadas ou nível de risco
col_filtro1, col_filtro2 = st.columns([1, 2])
with col_filtro1:
    filtro_risco = st.selectbox("Filtrar por nível:", ["Todos", "Crítico", "Alto", "Moderado", "Baixo"])

celulas_filtradas = (
    celulas if filtro_risco == "Todos"
    else [c for c in celulas if c["nivel_risco"] == filtro_risco]
)

if not celulas_filtradas:
    st.info("Nenhuma célula encontrada com este filtro de risco.")
    st.stop()

with col_filtro2:
    opcoes_celula = {
        f"Lat: {c['latitude']:.4f}, Lon: {c['longitude']:.4f} — Risco: {c['nivel_risco']} ({c['pontuacao_risco']:.1f})": c
        for c in celulas_filtradas
    }
    celula_nome = st.selectbox("Selecione a Célula Geográfica:", list(opcoes_celula.keys()))
    celula = opcoes_celula[celula_nome]

st.divider()

# Métricas da Célula Selecionada
col_resumo, col_radar = st.columns([3, 2])

with col_resumo:
    st.markdown(f"### Célula em Lat: `{celula['latitude']}`, Lon: `{celula['longitude']}`")
    
    cor_map = {"Crítico": "🔴", "Alto": "🟠", "Moderado": "🟡", "Baixo": "🟢"}
    st.markdown(f"**Classificação:** {cor_map.get(celula['nivel_risco'], '')} **{celula['nivel_risco']}** (Score: {celula['pontuacao_risco']}/100)")
    
    st.info(f"**Diagnóstico Científico:** {celula.get('justificativa', 'Sem justificativa disponível.')}")

    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            label="🌿 NDVI (Vigor Vegetativo)",
            value=f"{celula['ndvi']:.3f}",
            help="Normalizado entre -1 e +1. Valores < 0.2 indicam vegetação muito ressecada ou solo exposto."
        )
        st.metric(
            label="💧 NDII (Água na Copa Foliar)",
            value=f"{celula['ndii']:.3f}",
            help="Mede o estresse hídrico. Valores baixos apontam copa desidratada propensa a inflamar."
        )

    with c2:
        st.metric(
            label="🔥 NBR (Razão Normalizada de Queima)",
            value=f"{celula['nbr']:.3f}",
            help="Contraste NIR/SWIR2. Valores baixos indicam alta suscetibilidade térmica."
        )
        st.metric(
            label="🍂 PSRI (Índice de Senescência)",
            value=f"{celula['psri']:.3f}",
            help="Razão carotenoide/clorofila. Valores altos (> 0.1) revelam biomassa morta/combustível."
        )

with col_radar:
    st.plotly_chart(plot_radar_indices(celula), use_container_width=True)

st.divider()

# Metadados do Satélite e da Cena Orbital
st.markdown("### Metadados da Cena Orbital e Condições de Aquisição")
meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
with meta_col1:
    st.write("**Plataforma Orbital:**")
    st.code(analise.get("satelite", "Sentinel-2 MSI"))
with meta_col2:
    st.write("**Identificador da Cena:**")
    st.code(analise.get("id_cena_satelite", "S2A_MSIL2A"))
with meta_col3:
    st.write("**Data de Referência:**")
    st.code(analise.get("data_referencia", "")[:10])
with meta_col4:
    st.write("**Resolução Espacial:**")
    st.code("10m (B2, B4, B8) / 20m (B11, B12)")

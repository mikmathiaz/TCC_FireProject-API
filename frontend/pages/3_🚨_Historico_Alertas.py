"""
Tela 3: Painel de Histórico e Alertas — Validação Cruzada com INPE
"""

import streamlit as st
import pandas as pd
from frontend.services.api_client import api_client

st.set_page_config(page_title="Histórico e Validação — Fire Watcher", page_icon="🚨", layout="wide")

st.title("🚨 Histórico de Análises e Validação Cruzada (INPE)")

st.markdown("""
Esta tela consolida as análises temporais e realiza o confronto científico entre as zonas 
de alto risco identificadas pelo **Fire Watcher (Sentinel-2)** e os focos de calor reais 
reportados pelo **BDQueimadas/INPE**.
""")

historico = api_client.get_analysis_history()
if not historico:
    st.info("Nenhuma análise processada ainda. Vá até a aba 'Configurações' para rodar uma análise.")
    st.stop()

# Tabela Geral de Histórico de Análises
st.markdown("### 📋 Análises Realizadas")
df_historico = pd.DataFrame(historico)
df_historico_show = df_historico[[
    "id", "data_referencia", "satelite", "classificacao_geral",
    "pontuacao_risco_media", "total_celulas", "celulas_alto_risco", "processada_em"
]].copy()
df_historico_show["data_referencia"] = df_historico_show["data_referencia"].str[:10]
df_historico_show["processada_em"] = df_historico_show["processada_em"].str[:19]
df_historico_show.columns = [
    "ID", "Data Imagem", "Sensor", "Risco Geral",
    "Score Médio", "Total Células", "Células Alerta", "Processado em"
]

st.dataframe(df_historico_show, use_container_width=True)

st.divider()

# Módulo de Validação Cruzada Científica
st.markdown("### 🔬 Validação Cruzada contra Focos do INPE")

col_v1, col_v2 = st.columns([2, 1])

with col_v1:
    analises_dict = {
        f"Análise #{h['id']} ({h['data_referencia'][:10]} - Risco: {h['classificacao_geral']})": h['id']
        for h in historico
    }
    analise_id_validar = st.selectbox("Selecione a análise para confrontar com o BDQueimadas:", list(analises_dict.keys()))
    id_selecionado = analises_dict[analise_id_validar]

with col_v2:
    raio_tolerancia = st.slider(
        "Raio de tolerância espacial (metros):",
        min_value=200,
        max_value=3000,
        value=1000,
        step=100,
        help="Distância máxima considerada entre o foco de calor do INPE e uma célula de risco do Sentinel-2."
    )

if st.button("🚀 Executar Validação Cruzada", type="primary"):
    with st.spinner("Cruzando coordenadas espaciais com a base de focos do INPE..."):
        res = api_client.run_cross_validation(id_selecionado, tolerance_m=float(raio_tolerancia))
        if res:
            st.success("Validação cruzada executada com sucesso!")
        else:
            st.error("Não foi possível executar a validação. Certifique-se de que há focos cadastrados.")

# Exibição dos Relatórios de Validação Cruzada Salvos
validacoes = api_client.get_validation_history()
if validacoes:
    st.markdown("#### Relatórios de Acurácia da Validação")
    df_val = pd.DataFrame(validacoes)
    df_val_show = df_val[[
        "id", "analise_id", "total_focos_inpe_detectados",
        "focos_em_zona_alto_risco", "taxa_coincidencia_percentual",
        "distancia_media_foco_zona_metros", "executada_em"
    ]].copy()
    df_val_show["executada_em"] = df_val_show["executada_em"].str[:19]
    df_val_show.columns = [
        "ID Validação", "ID Análise", "Total Focos INPE",
        "Focos em Zona de Risco", "Taxa de Acerto (%)", "Distância Média (m)", "Data Execução"
    ]
    st.dataframe(df_val_show, use_container_width=True)

    # Destaque de métricas da última validação
    ultima = validacoes[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Taxa de Coincidência (Acerto)", f"{ultima['taxa_coincidencia_percentual']:.1f}%")
    c2.metric("Focos em Zona de Risco", f"{ultima['focos_em_zona_alto_risco']} de {ultima['total_focos_inpe_detectados']}")
    c3.metric("Distância Média ao Risco", f"{ultima.get('distancia_media_foco_zona_metros', 0):.0f} metros")
else:
    st.info("Nenhuma validação cruzada realizada ainda. Clique no botão acima para confrontar os dados.")

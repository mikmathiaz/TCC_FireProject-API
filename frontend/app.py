"""
Fire Watcher — Aplicação Principal Streamlit
Trabalho de Conclusão de Curso (TCC II) em Engenharia da Computação
"""

import streamlit as st
from frontend.services.api_client import api_client

st.set_page_config(
    page_title="Fire Watcher — Monitoramento de Queimadas",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header & Contexto Acadêmico
st.title("🛰️ Fire Watcher")
st.subheader("Sistema de Monitoramento Inteligente e Detecção Precoce de Queimadas")

st.markdown("""
> **Trabalho de Conclusão de Curso (TCC II) — Engenharia da Computação**  
> Proposta complementar ao BDQueimadas/INPE baseada em sensoriamento remoto orbital refinado (**Sentinel-2 MSI**) 
> e cálculo multiespectral de suscetibilidade à queima (**NBR, NDVI, NDII e PSRI**).
""")

# Status do Backend FastAPI
status = api_client.check_health()
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if status.get("online"):
        st.success(f"🟢 **Backend API Conectado** ({status['data'].get('versao', '1.0')})")
    else:
        st.error("🔴 **Backend Desconectado** — Inicie o servidor FastAPI na porta 8000")

with col2:
    aois = api_client.get_aois()
    st.info(f"📍 **Áreas Cadastradas:** {len(aois)}")

with col3:
    analises = api_client.get_analysis_history()
    st.info(f"📊 **Análises Processadas:** {len(analises)}")

st.divider()

# Cartões de Navegação Rápida
st.markdown("### Módulos do Sistema")

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown("""
    #### 🗺️ 1. Dashboard Principal
    Visualização cartográfica da Área de Interesse, mapa de calor das células de risco e sobreposição dos focos do INPE.
    """)
    st.page_link("pages/1_🗺️_Dashboard_Principal.py", label="Ir para o Dashboard", icon="🗺️")

with col_b:
    st.markdown("""
    #### 📊 2. Detalhamento de Área
    Inspeção minuciosa dos 4 índices espectrais, justificativas biofísicas e perfil de risco por célula.
    """)
    st.page_link("pages/2_📊_Detalhamento_Area.py", label="Ir para Detalhamento", icon="📊")

with col_c:
    st.markdown("""
    #### 🚨 3. Histórico e Alertas
    Registro cronológico de detecções e validação cruzada estatística contra a base oficial do INPE.
    """)
    st.page_link("pages/3_🚨_Historico_Alertas.py", label="Ir para Histórico", icon="🚨")

with col_d:
    st.markdown("""
    #### ⚙️ 4. Configurações & Execução
    Definição de novas AOIs, escolha de período temporal e disparo de novas rotinas de processamento.
    """)
    st.page_link("pages/4_⚙️_Configuracoes.py", label="Ir para Configurações", icon="⚙️")

st.divider()

# Resumo Teórico dos 4 Índices para a Banca
with st.expander("📚 Fundamentação Teórica dos Índices Espectrais (Para Defesa na Banca)"):
    st.markdown("""
    1. **NDVI (Normalized Difference Vegetation Index):**
       $$\\text{NDVI} = \\frac{B8 - B4}{B8 + B4}$$
       *Vigor fotossintético e biomassa ativa.* Valores baixos revelam vegetação ressecada ou solo exposto.
    
    2. **NBR (Normalized Burn Ratio):**
       $$\\text{NBR} = \\frac{B8 - B12}{B8 + B12}$$
       *Sensibilidade direta à perda de água celular e cicatrizes térmicas.* O SWIR-2 absorve em presença de água e reflete fortemente em solo calcinado/seco.
    
    3. **NDII (Normalized Difference Infrared Index):**
       $$\\text{NDII} = \\frac{B8 - B11}{B8 + B11}$$
       *Conteúdo relativo de água na copa vegetal (*canopy water content*).* Excelente preditor de estresse hídrico pré-ignição.
    
    4. **PSRI (Plant Senescence Reflectance Index):**
       $$\\text{PSRI} = \\frac{B4 - B2}{B8}$$
       *Degradação de clorofila versus acúmulo de carotenoides.* Valores elevados apontam biomassa vegetal morta ou senescente pronta para propagar chamas.
    """)

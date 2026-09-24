"""
Tela 4: Configuração e Execução de Processamento — Fire Watcher
"""

import streamlit as st
from datetime import date, timedelta
from frontend.services.api_client import api_client

st.set_page_config(page_title="Configurações — Fire Watcher", page_icon="⚙️", layout="wide")

st.title("⚙️ Configurações e Disparo de Processamento")

tab_execucao, tab_aoi, tab_inpe = st.tabs([
    "🛰️ Disparo de Nova Análise",
    "📍 Gerenciamento de AOIs",
    "🔥 Base de Dados do INPE"
])

# ----------------- TAB 1: Disparo de Nova Análise -----------------
with tab_execucao:
    st.markdown("### Processamento Multiespectral Sentinel-2")
    st.markdown("Selecione a Área de Interesse e o intervalo temporal para ingestão e cálculo dos índices.")

    aois = api_client.get_aois()
    if not aois:
        st.warning("Nenhuma AOI cadastrada.")
        st.stop()

    aoi_dict = {f"{a['nome']} (ID: {a['id']})": a["id"] for a in aois}
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        aoi_sel_nome = st.selectbox("Área de Interesse (AOI):", list(aoi_dict.keys()))
        aoi_id = aoi_dict[aoi_sel_nome]

    with col_e2:
        satelite_sel = st.selectbox("Sensor / Satélite:", ["Sentinel-2 MSI (Harmonized)", "Landsat-8/9 OLI"])

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        hoje = date.today()
        data_ini = st.date_input("Data de Início:", hoje - timedelta(days=15))
    with col_d2:
        data_fim = st.date_input("Data de Fim:", hoje)
    with col_d3:
        nuvens = st.slider("Cobertura máxima de nuvens (%):", 0, 50, 20)

    if st.button("🚀 Iniciar Processamento Espectral", type="primary"):
        payload = {
            "area_id": aoi_id,
            "data_inicio": str(data_ini),
            "data_fim": str(data_fim),
            "satelite": satelite_sel,
            "max_cobertura_nuvens": float(nuvens)
        }
        with st.spinner("Buscando bandas orbitais, calculando NBR, NDVI, NDII, PSRI e classificando zonas de risco..."):
            res = api_client.process_analysis(payload)
            if res:
                st.success(f"Análise #{res['id']} concluída com sucesso! Risco Geral: {res['classificacao_geral']}.")
                st.balloons()
            else:
                st.error("Falha ao processar análise. Verifique se o backend está ativo.")

# ----------------- TAB 2: Gerenciamento de AOIs -----------------
with tab_aoi:
    st.markdown("### Áreas de Interesse Cadastradas")
    for a in aois:
        with st.expander(f"📍 {a['nome']} (ID: {a['id']})"):
            st.write(f"**Descrição:** {a.get('descricao', 'Sem descrição.')}")
            st.write(f"**Bounding Box:** Latitudes [{a['min_lat']}, {a['max_lat']}] | Longitudes [{a['min_lon']}, {a['max_lon']}]")

    st.markdown("#### Cadastrar Nova Área de Interesse")
    with st.form("form_nova_aoi"):
        nome_aoi = st.text_input("Nome da Região/Parque:", placeholder="Ex: Parque Nacional da Chapada dos Veadeiros")
        desc_aoi = st.text_area("Descrição / Bioma:", placeholder="Ex: Região de Cerrado de altitude...")
        c_lat1, c_lat2 = st.columns(2)
        min_lat = c_lat1.number_input("Latitude Mínima (Sul):", value=-14.2500, format="%.4f")
        max_lat = c_lat2.number_input("Latitude Máxima (Norte):", value=-14.0000, format="%.4f")
        c_lon1, c_lon2 = st.columns(2)
        min_lon = c_lon1.number_input("Longitude Mínima (Oeste):", value=-47.8500, format="%.4f")
        max_lon = c_lon2.number_input("Longitude Máxima (Leste):", value=-47.5000, format="%.4f")

        btn_cadastrar = st.form_submit_button("Salvar Nova AOI")
        if btn_cadastrar:
            if not nome_aoi:
                st.error("O nome da AOI é obrigatório.")
            else:
                novo_payload = {
                    "nome": nome_aoi,
                    "descricao": desc_aoi,
                    "min_lat": float(min_lat),
                    "max_lat": float(max_lat),
                    "min_lon": float(min_lon),
                    "max_lon": float(max_lon)
                }
                criado = api_client.create_aoi(novo_payload)
                if criado:
                    st.success("Nova Área de Interesse cadastrada!")
                    st.rerun()
                else:
                    st.error("Erro ao cadastrar AOI. Verifique se o nome já não existe.")

# ----------------- TAB 3: Base do INPE -----------------
with tab_inpe:
    st.markdown("### Ingestão de Focos Históricos do BDQueimadas/INPE")
    st.markdown("""
    O sistema utiliza os focos oficiais do INPE para **validação cruzada científica**.
    Você pode carregar a base de amostra já inclusa no projeto para o Parque Nacional de Brasília.
    """)

    focos_atuais = api_client.get_inpe_focos(limit=10)
    st.info(f"Focos de calor atualmente no banco: {len(api_client.get_inpe_focos(limit=1000))}")

    if st.button("📥 Carregar Amostra Padrão do BDQueimadas (Brasília)"):
        with st.spinner("Importando CSV do INPE para o SQLite..."):
            ret = api_client.load_inpe_sample()
            if ret.get("status") == "sucesso":
                st.success(f"{ret.get('registros_importados', 0)} registros importados com sucesso!")
            else:
                st.error("Erro ao carregar amostra.")

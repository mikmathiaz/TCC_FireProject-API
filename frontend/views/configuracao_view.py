"""
View: Configurações e Disparo de Processamento — Fire Watcher
Apresenta o painel de configuração de AOIs, intervalo temporal e ingestão do INPE.
"""

import streamlit as st
from datetime import date, timedelta
from frontend.controllers.api_controller import api_controller


def render_configuracao_view():
    """
    Renderiza a interface de configurações e disparos.
    """
    st.markdown('<div class="section-title">Configurações e Parâmetros Operacionais</div>', unsafe_allow_html=True)

    tab_proc, tab_aoi, tab_inpe = st.tabs([
        "Processamento de Satélite",
        "Áreas de Interesse (AOIs)",
        "Base de Focos INPE"
    ])

    # TAB 1: Processamento de Satélite
    with tab_proc:
        st.markdown("#### Parâmetros para Ingestão Orbital")
        st.caption("Configura os limites temporais e a tolerância de cobertura de nuvens para o cálculo dos índices.")

        aois = api_controller.get_aois()
        if not aois:
            st.warning("Nenhuma AOI cadastrada.")
            return

        mapa_aois = {f"{a['nome']} (ID: {a['id']})": a["id"] for a in aois}

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            aoi_label = st.selectbox("Selecione a Área de Interesse (AOI):", list(mapa_aois.keys()))
            aoi_id = mapa_aois[aoi_label]

        with c_p2:
            satelite_sel = st.selectbox("Sensor / Plataforma:", ["Sentinel-2 MSI (Harmonized)", "Landsat-8/9 OLI"])

        c_d1, c_d2, c_d3 = st.columns(3)
        with c_d1:
            hoje = date.today()
            data_ini = st.date_input("Data de Início:", hoje - timedelta(days=15))
        with c_d2:
            data_fim = st.date_input("Data de Fim:", hoje)
        with c_d3:
            nuvens = st.slider("Cobertura Máxima de Nuvens (%):", 0, 50, 20)

        if st.button("Iniciar Processamento de Índices", type="primary"):
            payload = {
                "area_id": aoi_id,
                "data_inicio": str(data_ini),
                "data_fim": str(data_fim),
                "satelite": satelite_sel,
                "max_cobertura_nuvens": float(nuvens)
            }
            with st.spinner("Ingerindo bandas espectrais, calculando NBR, NDVI, NDII, PSRI e classificando risco..."):
                res = api_controller.process_analysis(payload)
                if res:
                    st.success(f"Análise #{res['id']} concluída com sucesso. Risco Geral: {res['classificacao_geral']}.")
                else:
                    st.error("Falha ao processar análise. Verifique a conectividade da API.")

    # TAB 2: Gerenciamento de AOIs
    with tab_aoi:
        st.markdown("#### Áreas de Interesse Monitoradas")
        for a in aois:
            with st.expander(f"AOI: {a['nome']} (ID: {a['id']})"):
                st.write(f"**Descrição:** {a.get('descricao', 'Sem descrição informada.')}")
                st.write(f"**Coordenadas Delimitadoras (Bounding Box):** Latitudes [{a['min_lat']}, {a['max_lat']}] | Longitudes [{a['min_lon']}, {a['max_lon']}]")

        st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### Cadastrar Nova Área de Interesse")
        with st.form("form_nova_aoi"):
            nome_aoi = st.text_input("Nome da Região / Parque:", placeholder="Ex: Parque Nacional da Chapada dos Veadeiros")
            desc_aoi = st.text_area("Descrição / Contexto Ambiental:", placeholder="Ex: Unidade de conservação no bioma Cerrado...")
            c_lat1, c_lat2 = st.columns(2)
            min_lat = c_lat1.number_input("Latitude Mínima (Sul):", value=-14.2500, format="%.4f")
            max_lat = c_lat2.number_input("Latitude Máxima (Norte):", value=-14.0000, format="%.4f")
            c_lon1, c_lon2 = st.columns(2)
            min_lon = c_lon1.number_input("Longitude Mínima (Oeste):", value=-47.8500, format="%.4f")
            max_lon = c_lon2.number_input("Longitude Máxima (Leste):", value=-47.5000, format="%.4f")

            btn_submit = st.form_submit_button("Salvar Área de Interesse")
            if btn_submit:
                if not nome_aoi.strip():
                    st.error("O nome da AOI é de preenchimento obrigatório.")
                else:
                    novo_payload = {
                        "nome": nome_aoi.strip(),
                        "descricao": desc_aoi.strip(),
                        "min_lat": float(min_lat),
                        "max_lat": float(max_lat),
                        "min_lon": float(min_lon),
                        "max_lon": float(max_lon)
                    }
                    criado = api_controller.create_aoi(novo_payload)
                    if criado:
                        st.success("Nova Área de Interesse cadastrada com sucesso.")
                        st.rerun()
                    else:
                        st.error("Erro ao cadastrar AOI. Verifique se o nome já não está em uso.")

    # TAB 3: Base de Focos INPE
    with tab_inpe:
        st.markdown("#### Ingestão de Focos Térmicos do BDQueimadas/INPE")
        st.caption("A base do INPE fornece as detecções operacionais utilizadas para confrontar a eficácia preditiva do sistema.")

        total_focos = len(api_controller.get_inpe_focos(limit=1000))
        st.info(f"Total de focos de calor atualmente registrados no banco local: {total_focos}")

        if st.button("Carregar Amostra Histórica do BDQueimadas (Brasília)"):
            with st.spinner("Importando planilha CSV para a base de dados SQLite..."):
                ret = api_controller.load_inpe_sample()
                if ret.get("status") == "sucesso":
                    st.success(f"{ret.get('registros_importados', 0)} registros importados com sucesso.")
                else:
                    st.error("Erro na importação da amostra.")

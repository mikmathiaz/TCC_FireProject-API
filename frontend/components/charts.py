"""
Componente de Gráficos Analíticos — Plotly
Renderiza gráficos de distribuição de risco, dispersão de bandas e perfil radar.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any


def plot_risk_distribution(celulas: List[Dict[str, Any]]) -> go.Figure:
    """
    Gera gráfico de distribuição percentual das classes de risco calculadas.
    """
    if not celulas:
        return go.Figure()

    df = pd.DataFrame(celulas)
    contagem = df["nivel_risco"].value_counts().reset_index()
    contagem.columns = ["Nivel", "Quantidade"]

    palette = {
        "Crítico": "#dc2626",
        "Alto": "#ea580c",
        "Moderado": "#ca8a04",
        "Baixo": "#16a34a"
    }

    fig = px.pie(
        contagem,
        values="Quantidade",
        names="Nivel",
        color="Nivel",
        color_discrete_map=palette,
        hole=0.5,
        title="Classificação de Risco (Percentual de Células)"
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        margin=dict(t=35, b=10, l=10, r=10),
        height=260,
        font=dict(family="sans-serif", size=11)
    )
    return fig


def plot_indices_dispersion(celulas: List[Dict[str, Any]]) -> go.Figure:
    """
    Gera gráfico boxplot da dispersão dos índices biofísicos na área de interesse.
    """
    if not celulas:
        return go.Figure()

    df = pd.DataFrame(celulas)
    fig = go.Figure()

    fig.add_trace(go.Box(y=df["ndvi"], name="NDVI", marker_color="#16a34a"))
    fig.add_trace(go.Box(y=df["nbr"], name="NBR", marker_color="#ea580c"))
    fig.add_trace(go.Box(y=df["ndii"], name="NDII", marker_color="#0284c7"))
    fig.add_trace(go.Box(y=df["psri"], name="PSRI", marker_color="#b45309"))

    fig.update_layout(
        title="Dispersão Estatística dos Índices Espectrais",
        yaxis_title="Valor Adimensional (-1 a +1)",
        margin=dict(t=35, b=10, l=10, r=10),
        height=260,
        font=dict(family="sans-serif", size=11)
    )
    return fig


def plot_radar_profile(celula: Dict[str, Any]) -> go.Figure:
    """
    Gera gráfico polar (radar) comparando o perfil espectral da célula selecionada.
    """
    labels = ["NDVI (Vigor)", "NBR (Ressecamento)", "NDII (Água Foliar)", "PSRI (Senescência)"]

    # Normalização para escala 0.0 a 1.0 para visualização polar uniforme
    v_ndvi = (celula.get("ndvi", 0.0) + 1.0) / 2.0
    v_nbr = (celula.get("nbr", 0.0) + 1.0) / 2.0
    v_ndii = (celula.get("ndii", 0.0) + 1.0) / 2.0
    v_psri = (celula.get("psri", 0.0) + 1.0) / 2.0

    valores = [v_ndvi, v_nbr, v_ndii, v_psri]
    valores.append(valores[0])
    labels_fechados = labels + [labels[0]]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=valores,
            theta=labels_fechados,
            fill="toself",
            name="Perfil Biofísico",
            line_color="#0284c7"
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        margin=dict(t=30, b=25, l=25, r=25),
        height=300,
        title="Assinatura Espectral da Célula"
    )
    return fig

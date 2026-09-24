"""
Componente de Gráficos e Visualização Científica — Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any


def plot_distribuicao_risco(celulas: List[Dict[str, Any]]) -> go.Figure:
    """
    Gera gráfico donut de distribuição percentual das classes de risco.
    """
    if not celulas:
        return go.Figure()

    df = pd.DataFrame(celulas)
    contagem = df["nivel_risco"].value_counts().reset_index()
    contagem.columns = ["Nível de Risco", "Quantidade"]

    cores = {
        "Crítico": "#D32F2F",
        "Alto": "#F57C00",
        "Moderado": "#FBC02D",
        "Baixo": "#2E7D32"
    }

    fig = px.pie(
        contagem,
        values="Quantidade",
        names="Nível de Risco",
        color="Nível de Risco",
        color_discrete_map=cores,
        hole=0.45,
        title="Distribuição das Zonas de Risco de Ignição"
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=300)
    return fig


def plot_radar_indices(celula: Dict[str, Any]) -> go.Figure:
    """
    Gera um gráfico radar comparando os valores normalizados dos 4 índices para uma célula.
    """
    categorias = ["NDVI (Vigor)", "NBR (Ressecamento)", "NDII (Água na Copa)", "PSRI (Senescência)"]

    # Normalização de apoio para visualização no radar (0 a 1)
    ndvi_norm = (celula.get("ndvi", 0.0) + 1.0) / 2.0
    nbr_norm = (celula.get("nbr", 0.0) + 1.0) / 2.0
    ndii_norm = (celula.get("ndii", 0.0) + 1.0) / 2.0
    psri_norm = (celula.get("psri", 0.0) + 1.0) / 2.0

    valores = [ndvi_norm, nbr_norm, ndii_norm, psri_norm]
    valores.append(valores[0])  # Fecha o círculo
    categorias_fechadas = categorias + [categorias[0]]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=valores,
            theta=categorias_fechadas,
            fill="toself",
            name="Perfil Espectral",
            line_color="#1E88E5"
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        margin=dict(t=30, b=30, l=30, r=30),
        height=320,
        title="Perfil Biofísico Espectral da Célula"
    )
    return fig


def plot_histograma_indices(celulas: List[Dict[str, Any]]) -> go.Figure:
    """
    Gera histogramas comparativos dos 4 índices espectrais para a área.
    """
    if not celulas:
        return go.Figure()

    df = pd.DataFrame(celulas)
    fig = go.Figure()

    fig.add_trace(go.Box(y=df["ndvi"], name="NDVI", marker_color="#2E7D32"))
    fig.add_trace(go.Box(y=df["nbr"], name="NBR", marker_color="#E65100"))
    fig.add_trace(go.Box(y=df["ndii"], name="NDII", marker_color="#0288D1"))
    fig.add_trace(go.Box(y=df["psri"], name="PSRI", marker_color="#D84315"))

    fig.update_layout(
        title="Dispersão dos Índices Biofísicos na Região",
        yaxis_title="Valor do Índice (-1 a +1)",
        margin=dict(t=40, b=10, l=10, r=10),
        height=320
    )
    return fig

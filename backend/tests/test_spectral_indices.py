"""
Testes unitários dos cálculos matemáticos dos índices espectrais.
Garantem conformidade com a literatura de sensoriamento remoto.
"""

import pytest
import numpy as np
from backend.app.services.spectral_indices import (
    calcular_ndvi,
    calcular_nbr,
    calcular_ndii,
    calcular_psri,
    calcular_todos_indices
)


def test_ndvi_vegetacao_vigorosa():
    """
    Vegetação vigorosa possui alta reflectância no NIR (B8) e baixa no Red (B4).
    O NDVI resultante deve ser expressivamente positivo (> 0.6).
    """
    nir = 0.50
    red = 0.08
    ndvi = calcular_ndvi(nir, red)
    assert 0.65 < ndvi < 0.80
    assert isinstance(ndvi, float)


def test_ndvi_solo_exposto():
    """
    Solo exposto possui reflectâncias similares no NIR e no Red.
    O NDVI deve ser baixo (< 0.25).
    """
    nir = 0.22
    red = 0.20
    ndvi = calcular_ndvi(nir, red)
    assert 0.0 <= ndvi < 0.20


def test_nbr_alta_umidade_vs_queimado():
    """
    NBR avalia a razão entre NIR e SWIR2.
    Áreas verdes possuem NBR alto; áreas queimadas/secas possuem NBR baixo/negativo.
    """
    # Vegetação densa e úmida
    nbr_verde = calcular_nbr(nir=0.45, swir2=0.10)
    assert nbr_verde > 0.60

    # Área seca / cicatriz de fogo (SWIR2 alto, NIR baixo)
    nbr_seco = calcular_nbr(nir=0.12, swir2=0.30)
    assert nbr_seco < -0.40


def test_ndii_conteudo_agua():
    """
    NDII mede a água foliar (NIR vs SWIR1).
    """
    ndii_hidratado = calcular_ndii(nir=0.40, swir1=0.15)
    ndii_estresse = calcular_ndii(nir=0.15, swir1=0.30)
    assert ndii_hidratado > 0.40
    assert ndii_estresse < -0.30


def test_psri_senescencia():
    """
    PSRI compara Red e Blue normalizado pelo NIR.
    Folhagem senescente (seca) eleva a reflectância no Red devido à perda de clorofila.
    """
    # Planta seca (alta senescência)
    psri_seca = calcular_psri(red=0.25, blue=0.10, nir=0.30)
    assert psri_seca > 0.40

    # Planta jovem/verde (baixa senescência)
    psri_verde = calcular_psri(red=0.04, blue=0.06, nir=0.50)
    assert psri_verde < 0.0


def test_divisao_por_zero_resiliente():
    """
    Verifica que valores nulos de reflectância não geram ZeroDivisionError nem crash.
    """
    assert calcular_ndvi(0.0, 0.0) == 0.0
    assert calcular_nbr(0.0, 0.0) == 0.0
    assert calcular_ndii(0.0, 0.0) == 0.0
    assert calcular_psri(0.0, 0.0, 0.0) == 0.0


def test_processamento_em_lote_numpy():
    """
    Valida a computação vetorizada sobre matrizes/arrays multidimensionais.
    """
    nir_arr = np.array([0.5, 0.2, 0.1])
    red_arr = np.array([0.1, 0.2, 0.3])
    resultado = calcular_ndvi(nir_arr, red_arr)
    assert len(resultado) == 3
    assert resultado[0] > 0.6
    assert abs(resultado[1]) < 0.05
    assert resultado[2] < 0.0

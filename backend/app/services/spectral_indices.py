"""
Módulo de Cálculo de Índices Espectrais — Fire Watcher
Implementação rigorosa das fórmulas biofísicas utilizadas para sensoriamento
remoto orbital (Sentinel-2 MSI) e detecção de suscetibilidade a queimadas.

Bandas Sentinel-2 de referência:
- B2 (Blue):  490 nm  (Resolução: 10m)
- B4 (Red):   665 nm  (Resolução: 10m)
- B8 (NIR):   842 nm  (Resolução: 10m)
- B11 (SWIR1): 1610 nm (Resolução: 20m)
- B12 (SWIR2): 2190 nm (Resolução: 20m)
"""

import numpy as np
from typing import Union

# Constante de estabilidade numérica para evitar divisão por zero
EPSILON = 1e-7


def calcular_ndvi(nir: Union[float, np.ndarray], red: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    NDVI — Normalized Difference Vegetation Index (Rouse et al., 1974)
    Fórmula: (NIR - Red) / (NIR + Red) -> (B8 - B4) / (B8 + B4)

    Significado Acadêmico:
    Avalia a densidade e o vigor da biomassa verde fotossinteticamente ativa.
    - Valores altos (> 0.5): Vegetação densa e saudável, com alta umidade foliar.
    - Valores moderados (0.2 a 0.5): Vegetação rala, pastagem ou savana em transição.
    - Valores baixos (< 0.2): Solo exposto, rocha ou vegetação severamente ressecada.
    """
    denominador = nir + red
    if isinstance(denominador, np.ndarray):
        denominador = np.where(denominador == 0, EPSILON, denominador)
        ndvi = (nir - red) / denominador
        return np.clip(ndvi, -1.0, 1.0)
    else:
        if abs(denominador) < EPSILON:
            return 0.0
        return float(np.clip((nir - red) / denominador, -1.0, 1.0))


def calcular_nbr(nir: Union[float, np.ndarray], swir2: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    NBR — Normalized Burn Ratio (Key & Benson, 2006)
    Fórmula: (NIR - SWIR2) / (NIR + SWIR2) -> (B8 - B12) / (B8 + B12)

    Significado Acadêmico:
    Utiliza a sensibilidade do infravermelho de ondas curtas (SWIR) à água
    e do NIR à estrutura celular das folhas.
    - Valores altos (> 0.4): Vegetação exuberante, alta umidade.
    - Valores intermediários (0.1 a 0.3): Umidade em declínio, risco moderado.
    - Valores baixos a negativos (< 0.1): Alta inflamabilidade, dessecação ou cicatriz recente.
    """
    denominador = nir + swir2
    if isinstance(denominador, np.ndarray):
        denominador = np.where(denominador == 0, EPSILON, denominador)
        nbr = (nir - swir2) / denominador
        return np.clip(nbr, -1.0, 1.0)
    else:
        if abs(denominador) < EPSILON:
            return 0.0
        return float(np.clip((nir - swir2) / denominador, -1.0, 1.0))


def calcular_ndii(nir: Union[float, np.ndarray], swir1: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    NDII — Normalized Difference Infrared Index / NDWI (Hardisky et al., 1983; Gao, 1996)
    Fórmula: (NIR - SWIR1) / (NIR + SWIR1) -> (B8 - B11) / (B8 + B11)

    Significado Acadêmico:
    Indicador direto do conteúdo relativo de água na copa da vegetação (Equivalent Water Thickness).
    - Valores positivos elevados (> 0.3): Copa bem hidratada.
    - Valores próximos de 0 ou negativos (< 0.0): Estresse hídrico severo na cobertura vegetal.
    """
    denominador = nir + swir1
    if isinstance(denominador, np.ndarray):
        denominador = np.where(denominador == 0, EPSILON, denominador)
        ndii = (nir - swir1) / denominador
        return np.clip(ndii, -1.0, 1.0)
    else:
        if abs(denominador) < EPSILON:
            return 0.0
        return float(np.clip((nir - swir1) / denominador, -1.0, 1.0))


def calcular_psri(
    red: Union[float, np.ndarray],
    blue: Union[float, np.ndarray],
    nir: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    PSRI — Plant Senescence Reflectance Index (Merzlyak et al., 1999)
    Fórmula: (Red - Blue) / NIR -> (B4 - B2) / B8

    Significado Acadêmico:
    Mede a razão entre pigmentos de carotenoides e clorofila. Durante o envelhecimento
    e secagem da planta (senescência), a clorofila degrada-se mais rapidamente que os carotenoides.
    - Valores baixos ou negativos (< 0.0): Vegetação jovem, vigorosa e não senescente.
    - Valores elevados (> 0.1 a 0.3): Folhagem seca, morta ou em processo acelerado de senescência,
      constituindo material fino combustível de ignição imediata.
    """
    denominador = nir
    if isinstance(denominador, np.ndarray):
        denominador = np.where(denominador == 0, EPSILON, denominador)
        psri = (red - blue) / denominador
        return np.clip(psri, -1.0, 1.0)
    else:
        if abs(denominador) < EPSILON:
            return 0.0
        return float(np.clip((red - blue) / denominador, -1.0, 1.0))


def calcular_todos_indices(b2_blue: float, b4_red: float, b8_nir: float, b11_swir1: float, b12_swir2: float) -> dict:
    """
    Calcula simultaneamente os quatro índices espectrais para um pixel/célula
    a partir das reflectâncias de superfície (BOA - Bottom of Atmosphere).
    """
    return {
        "ndvi": round(calcular_ndvi(b8_nir, b4_red), 4),
        "nbr": round(calcular_nbr(b8_nir, b12_swir2), 4),
        "ndii": round(calcular_ndii(b8_nir, b11_swir1), 4),
        "psri": round(calcular_psri(b4_red, b2_blue, b8_nir), 4),
    }

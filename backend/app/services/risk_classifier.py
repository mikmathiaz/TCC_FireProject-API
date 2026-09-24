"""
Módulo de Classificação de Zonas de Risco de Ignição — Fire Watcher
Compara os índices biofísicos com limiares acadêmicos para estimar
a probabilidade de ignição e combustibilidade da biomassa.

Os limiares foram desenhados de forma modular e parametrizável, permitindo
calibração futura com base no artigo de 2025 do pesquisador do INPE.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class LimiaresRisco:
    """
    Limiares críticos de referência na literatura para vegetação de Cerrado / Savana.
    Podem ser sobrescritos dinamicamente para calibração acadêmica.
    """
    # NDVI (Vigor): abaixo destes valores indica vegetação rala/seca
    ndvi_critico: float = 0.20
    ndvi_alto: float = 0.35
    ndvi_moderado: float = 0.50

    # NBR (Umidade foliar / Cicatriz): abaixo destes valores indica alta suscetibilidade
    nbr_critico: float = 0.05
    nbr_alto: float = 0.20
    nbr_moderado: float = 0.35

    # NDII (Conteúdo de água na copa): abaixo destes valores indica dessecação severa
    ndii_critico: float = -0.05
    ndii_alto: float = 0.10
    ndii_moderado: float = 0.25

    # PSRI (Senescência): acima destes valores indica biomassa combustível seca
    psri_critico: float = 0.18
    psri_alto: float = 0.10
    psri_moderado: float = 0.02


def classificar_risco(
    ndvi: float,
    nbr: float,
    ndii: float,
    psri: float,
    limiares: LimiaresRisco = LimiaresRisco()
) -> Dict[str, Any]:
    """
    Avalia a combinação dos 4 índices espectrais e retorna:
    - nivel_risco: 'Baixo' | 'Moderado' | 'Alto' | 'Crítico'
    - pontuacao_risco: 0.0 a 100.0
    - justificativa: texto acadêmico detalhado
    """
    # Cálculo de sub-pontuações de risco para cada índice (0 a 100)
    # 1. NDVI: menor valor = maior risco
    if ndvi <= limiares.ndvi_critico:
        score_ndvi = 95.0
    elif ndvi <= limiares.ndvi_alto:
        score_ndvi = 75.0
    elif ndvi <= limiares.ndvi_moderado:
        score_ndvi = 45.0
    else:
        score_ndvi = 15.0

    # 2. NBR: menor valor = maior risco
    if nbr <= limiares.nbr_critico:
        score_nbr = 100.0
    elif nbr <= limiares.nbr_alto:
        score_nbr = 80.0
    elif nbr <= limiares.nbr_moderado:
        score_nbr = 45.0
    else:
        score_nbr = 10.0

    # 3. NDII: menor valor = menor água foliar = maior risco
    if ndii <= limiares.ndii_critico:
        score_ndii = 95.0
    elif ndii <= limiares.ndii_alto:
        score_ndii = 75.0
    elif ndii <= limiares.ndii_moderado:
        score_ndii = 40.0
    else:
        score_ndii = 10.0

    # 4. PSRI: maior valor = maior senescência = maior risco
    if psri >= limiares.psri_critico:
        score_psri = 95.0
    elif psri >= limiares.psri_alto:
        score_psri = 75.0
    elif psri >= limiares.psri_moderado:
        score_psri = 45.0
    else:
        score_psri = 15.0

    # Média ponderada dos fatores (NBR e NDII têm maior peso na inflamabilidade direta)
    # Pesos: NBR (0.35), NDII (0.30), PSRI (0.20), NDVI (0.15)
    pontuacao = (
        (score_nbr * 0.35) +
        (score_ndii * 0.30) +
        (score_psri * 0.20) +
        (score_ndvi * 0.15)
    )
    pontuacao = round(min(100.0, max(0.0, pontuacao)), 2)

    # Classificação categórica
    if pontuacao >= 80.0:
        nivel = "Crítico"
        justificativa = (
            f"Combinação de severo estresse hídrico (NDII: {ndii:.2f}), dessecação acentuada "
            f"(NBR: {nbr:.2f}) e senescência avançada (PSRI: {psri:.2f}), configurando combustível "
            f"com alto potencial de ignição imediata."
        )
    elif pontuacao >= 60.0:
        nivel = "Alto"
        justificativa = (
            f"Vegetação em transição com baixa umidade foliar (NBR: {nbr:.2f}, NDII: {ndii:.2f}) "
            f"e biomassa seca em expansão (PSRI: {psri:.2f})."
        )
    elif pontuacao >= 35.0:
        nivel = "Moderado"
        justificativa = (
            f"Índices moderados de biomassa (NDVI: {ndvi:.2f}) e umidade estável. "
            f"Monitoramento preventivo recomendado."
        )
    else:
        nivel = "Baixo"
        justificativa = (
            f"Vegetação verde e saudável (NDVI: {ndvi:.2f}, NBR: {nbr:.2f}) com copa bem "
            f"hidratada (NDII: {ndii:.2f}), conferindo alta resiliência ao fogo."
        )

    return {
        "nivel_risco": nivel,
        "pontuacao_risco": pontuacao,
        "justificativa": justificativa,
        "sub_scores": {
            "ndvi": score_ndvi,
            "nbr": score_nbr,
            "ndii": score_ndii,
            "psri": score_psri
        }
    }

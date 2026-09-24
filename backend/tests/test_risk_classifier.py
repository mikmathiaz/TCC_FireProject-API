"""
Testes unitários para o classificador de risco de queimadas.
"""

from backend.app.services.risk_classifier import classificar_risco, LimiaresRisco


def test_classificacao_zona_critica():
    """
    Combinação de índices desfavoráveis (seca extrema + senescência alta)
    deve resultar em risco 'Crítico' e pontuação >= 80.
    """
    res = classificar_risco(
        ndvi=0.15,   # Vegetação muito seca
        nbr=-0.10,   # Baixa umidade / cicatriz
        ndii=-0.20,  # Estresse hídrico agudo
        psri=0.35    # Alta senescência
    )
    assert res["nivel_risco"] == "Crítico"
    assert res["pontuacao_risco"] >= 80.0
    assert "estresse hídrico" in res["justificativa"]


def test_classificacao_zona_baixa():
    """
    Vegetação vigorosa e copa hidratada deve resultar em risco 'Baixo'.
    """
    res = classificar_risco(
        ndvi=0.72,   # Vigor exuberante
        nbr=0.65,    # Umidade abundante
        ndii=0.45,   # Alta água na copa
        psri=-0.05   # Planta sem senescência
    )
    assert res["nivel_risco"] == "Baixo"
    assert res["pontuacao_risco"] < 35.0


def test_limiares_customizaveis():
    """
    Garante que é possível calibrar os limiares com parâmetros acadêmicos específicos.
    """
    limiares_estritos = LimiaresRisco(
        ndvi_critico=0.30,
        nbr_critico=0.15,
        ndii_critico=0.05,
        psri_critico=0.10
    )
    res = classificar_risco(
        ndvi=0.25,
        nbr=0.10,
        ndii=0.00,
        psri=0.12,
        limiares=limiares_estritos
    )
    assert res["nivel_risco"] in ["Alto", "Crítico"]

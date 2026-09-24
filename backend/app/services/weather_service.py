"""
Serviço de Dados Meteorológicos Complementares — Open-Meteo API
Consulta temperatura, umidade relativa do ar, velocidade do vento e precipitação.
Permite enriquecer a análise de satélite com as condições atmosféricas imediatas.
"""

import httpx
from typing import Dict, Any
from backend.app.core.config import settings


def calcular_risco_meteorologico(temperatura: float, umidade: float, vento_kmh: float, precipitacao: float) -> float:
    """
    Calcula um índice sintético de perigo meteorológico (0 a 100), inspirado
    na clássica 'Regra dos 30' (Temperatura > 30°C, Umidade < 30%, Vento > 30 km/h)
    e no Fire Weather Index (FWI).
    """
    # Fator Temperatura (pesa positivamente o risco)
    fator_temp = max(0.0, min(100.0, (temperatura - 15.0) * 3.5))

    # Fator Umidade Relativa (menor umidade = ar mais seco = maior risco)
    fator_umid = max(0.0, min(100.0, (80.0 - umidade) * 1.5))

    # Fator Vento (oxigenação e propagação)
    fator_vento = max(0.0, min(100.0, vento_kmh * 2.5))

    # Penalidade por chuva recente
    fator_chuva = max(0.0, 100.0 - (precipitacao * 20.0)) / 100.0

    score = ((fator_temp * 0.35) + (fator_umid * 0.40) + (fator_vento * 0.25)) * fator_chuva
    return round(float(max(0.0, min(100.0, score))), 2)


async def obter_clima_atual(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Consulta a API pública e aberta Open-Meteo para as coordenadas fornecidas.
    Não requer chave de API privada.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
            "weather_code"
        ],
        "timezone": "America/Sao_Paulo"
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(settings.OPEN_METEO_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})

            temp = float(current.get("temperature_2m", 25.0))
            umid = float(current.get("relative_humidity_2m", 50.0))
            vento = float(current.get("wind_speed_10m", 10.0))
            precip = float(current.get("precipitation", 0.0))
            dir_vento = float(current.get("wind_direction_10m", 0.0))

            risco_met = calcular_risco_meteorologico(temp, umid, vento, precip)

            return {
                "latitude": latitude,
                "longitude": longitude,
                "temperatura_atual": temp,
                "umidade_relativa_atual": umid,
                "velocidade_vento_atual": vento,
                "direcao_vento_atual": dir_vento,
                "precipitacao_recente": precip,
                "condicao_tempo": f"Código WMO {current.get('weather_code', 0)}",
                "indice_risco_meteorologico": risco_met
            }
    except Exception as e:
        # Fallback resiliente caso haja indisponibilidade de rede
        return {
            "latitude": latitude,
            "longitude": longitude,
            "temperatura_atual": 28.0,
            "umidade_relativa_atual": 45.0,
            "velocidade_vento_atual": 15.0,
            "direcao_vento_atual": 180.0,
            "precipitacao_recente": 0.0,
            "condicao_tempo": "Modo offline / estimativa regional",
            "indice_risco_meteorologico": 52.0
        }

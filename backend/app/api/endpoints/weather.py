"""
Endpoints de meteorologia (Open-Meteo API).
"""

from fastapi import APIRouter, Query
from backend.app.schemas.schemas import WeatherDataResponse
from backend.app.services.weather_service import obter_clima_atual

router = APIRouter(prefix="/weather", tags=["Condições Meteorológicas"])


@router.get("/current", response_model=WeatherDataResponse)
async def obter_clima(
    latitude: float = Query(..., description="Latitude do ponto ou centroide da AOI"),
    longitude: float = Query(..., description="Longitude do ponto ou centroide da AOI")
):
    """
    Retorna os dados meteorológicos atuais da estação mais próxima (via Open-Meteo)
    e o índice de risco meteorológico de propagação.
    """
    dados = await obter_clima_atual(latitude, longitude)
    return dados

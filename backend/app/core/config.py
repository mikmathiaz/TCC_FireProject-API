"""
Configurações da aplicação Fire Watcher.
Carrega variáveis de ambiente ou utiliza valores padrão seguros para desenvolvimento.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    
    # Configurações da API FastAPI
    API_TITLE: str = "Fire Watcher API"
    API_DESCRIPTION: str = (
        "API para cálculo de índices espectrais (Sentinel-2), classificação "
        "de zonas de risco de queimadas e validação cruzada com o BDQueimadas/INPE."
    )
    API_VERSION: str = "1.0.0"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    # Banco de dados SQLite
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'fire_watcher.db'}"
    
    # Google Earth Engine
    GEE_PROJECT_ID: str = ""
    
    # Open-Meteo API
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    
    # Frontend
    BACKEND_API_URL: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

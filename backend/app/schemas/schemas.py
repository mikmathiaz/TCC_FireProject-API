"""
Esquemas Pydantic para validação e serialização de dados na API FastAPI.
"""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field


# --- Schemas de Área de Interesse (AOI) ---
class AreaInteresseBase(BaseModel):
    nome: str = Field(..., max_length=120, description="Nome identificador da AOI")
    descricao: Optional[str] = Field(None, description="Descrição ou contexto da unidade de conservação")
    min_lat: float = Field(..., description="Latitude mínima (sul)")
    max_lat: float = Field(..., description="Latitude máxima (norte)")
    min_lon: float = Field(..., description="Longitude mínima (oeste)")
    max_lon: float = Field(..., description="Longitude máxima (leste)")


class AreaInteresseCreate(AreaInteresseBase):
    geojson_geometry: Optional[str] = None


class AreaInteresseResponse(AreaInteresseBase):
    id: int
    geojson_geometry: Optional[str] = None
    criada_em: datetime

    class Config:
        from_attributes = True


# --- Schemas de Índices Espectrais ---
class IndiceEspectralResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    ndvi: float
    nbr: float
    ndii: float
    psri: float
    nivel_risco: str
    pontuacao_risco: float
    justificativa: Optional[str] = None

    class Config:
        from_attributes = True


# --- Schemas de Análise de Risco ---
class ProcessarAnaliseRequest(BaseModel):
    area_id: int = Field(..., description="ID da Área de Interesse cadastrada")
    data_inicio: date = Field(..., description="Data inicial do intervalo de busca")
    data_fim: date = Field(..., description="Data final do intervalo de busca")
    satelite: str = Field(default="Sentinel-2", description="Satélite de sensoriamento remoto")
    max_cobertura_nuvens: float = Field(default=20.0, description="Percentual máximo de nuvens tolerado")


class AnaliseRiscoResponse(BaseModel):
    id: int
    area_id: int
    data_referencia: datetime
    satelite: str
    id_cena_satelite: Optional[str] = None
    classificacao_geral: str
    pontuacao_risco_media: float
    total_celulas: int
    celulas_alto_risco: int
    processada_em: datetime

    class Config:
        from_attributes = True


class AnaliseRiscoDetailResponse(AnaliseRiscoResponse):
    area: AreaInteresseResponse
    indices: List[IndiceEspectralResponse] = []

    class Config:
        from_attributes = True


# --- Schemas de Focos de Calor INPE ---
class FocoINPEResponse(BaseModel):
    id: int
    data_hora: datetime
    satelite: str
    latitude: float
    longitude: float
    bioma: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[str] = None
    dias_sem_chuva: Optional[int] = None
    precipitacao: Optional[float] = None
    risco_fogo_inpe: Optional[float] = None
    frp: Optional[float] = None

    class Config:
        from_attributes = True


# --- Schemas de Validação Cruzada ---
class ValidacaoCruzadaResponse(BaseModel):
    id: int
    analise_id: int
    total_focos_inpe_detectados: int
    focos_em_zona_alto_risco: int
    taxa_coincidencia_percentual: float
    distancia_media_foco_zona_metros: Optional[float] = None
    executada_em: datetime

    class Config:
        from_attributes = True


# --- Schemas de Dados Meteorológicos (Open-Meteo) ---
class WeatherDataResponse(BaseModel):
    latitude: float
    longitude: float
    temperatura_atual: float
    umidade_relativa_atual: float
    velocidade_vento_atual: float
    direcao_vento_atual: float
    precipitacao_recente: float
    condicao_tempo: str
    indice_risco_meteorologico: float = Field(
        ..., description="Índice sintético de risco de propagação pelo clima (0 a 100)"
    )

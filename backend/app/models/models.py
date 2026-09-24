"""
Modelos de dados persistidos no banco SQLite via SQLAlchemy.
Representam Áreas de Interesse (AOI), análises de risco calculadas,
índices espectrais por ponto e histórico de focos do INPE para validação.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class AreaInteresse(Base):
    """
    Representa uma Área de Interesse (AOI) monitorada pelo sistema.
    """
    __tablename__ = "areas_interesse"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    
    # Bounding Box (Caixa delimitadora para corte de imagens orbitais)
    min_lat = Column(Float, nullable=False)
    max_lat = Column(Float, nullable=False)
    min_lon = Column(Float, nullable=False)
    max_lon = Column(Float, nullable=False)
    
    # Geometria detalhada em GeoJSON (opcional para polígonos complexos)
    geojson_geometry = Column(Text, nullable=True)
    
    criada_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com análises
    analises = relationship("AnaliseRisco", back_populates="area", cascade="all, delete-orphan")


class AnaliseRisco(Base):
    """
    Registro de uma execução de análise de risco para uma área e data específicas.
    """
    __tablename__ = "analises_risco"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas_interesse.id"), nullable=False)
    
    data_referencia = Column(DateTime, nullable=False, index=True)
    satelite = Column(String(50), default="Sentinel-2 MSI")
    id_cena_satelite = Column(String(100), nullable=True)
    
    # Síntese dos resultados
    classificacao_geral = Column(String(30), nullable=False)  # Baixo, Moderado, Alto, Crítico
    pontuacao_risco_media = Column(Float, nullable=False)     # Escala de 0 a 100
    total_celulas = Column(Integer, default=0)
    celulas_alto_risco = Column(Integer, default=0)
    
    processada_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    area = relationship("AreaInteresse", back_populates="analises")
    indices = relationship("IndiceEspectral", back_populates="analise", cascade="all, delete-orphan")
    validacoes = relationship("ValidacaoCruzada", back_populates="analise", cascade="all, delete-orphan")


class IndiceEspectral(Base):
    """
    Valores dos quatro índices espectrais (NBR, NDVI, NDII, PSRI) calculados
    para uma célula geográfica específica.
    """
    __tablename__ = "indices_espectrais"

    id = Column(Integer, primary_key=True, index=True)
    analise_id = Column(Integer, ForeignKey("analises_risco.id"), nullable=False, index=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Índices biofísicos calculados
    ndvi = Column(Float, nullable=False)   # Vigor vegetativo
    nbr = Column(Float, nullable=False)    # Suscetibilidade à queima / queima recente
    ndii = Column(Float, nullable=False)   # Conteúdo hídrico foliar
    psri = Column(Float, nullable=False)   # Nível de senescência da vegetação
    
    # Classificação calculada para o ponto
    nivel_risco = Column(String(30), nullable=False)  # Baixo, Moderado, Alto, Crítico
    pontuacao_risco = Column(Float, nullable=False)   # 0 a 100
    justificativa = Column(Text, nullable=True)       # Explicação analítica legível

    analise = relationship("AnaliseRisco", back_populates="indices")


class FocoINPE(Base):
    """
    Foco de calor registrado pelo Programa Queimadas do INPE (BDQueimadas).
    Utilizado como ground truth para validação cruzada.
    """
    __tablename__ = "focos_inpe"

    id = Column(Integer, primary_key=True, index=True)
    data_hora = Column(DateTime, nullable=False, index=True)
    satelite = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    bioma = Column(String(50), nullable=True)
    municipio = Column(String(100), nullable=True)
    estado = Column(String(50), nullable=True)
    
    dias_sem_chuva = Column(Integer, nullable=True)
    precipitacao = Column(Float, nullable=True)
    risco_fogo_inpe = Column(Float, nullable=True)
    frp = Column(Float, nullable=True)  # Fire Radiative Power (MW)


class ValidacaoCruzada(Base):
    """
    Resultado estatístico do cruzamento entre as zonas de risco previstas
    pelo Fire Watcher e os focos de calor reais registrados pelo INPE.
    """
    __tablename__ = "validacoes_cruzadas"

    id = Column(Integer, primary_key=True, index=True)
    analise_id = Column(Integer, ForeignKey("analises_risco.id"), nullable=False)
    
    total_focos_inpe_detectados = Column(Integer, nullable=False)
    focos_em_zona_alto_risco = Column(Integer, nullable=False)
    taxa_coincidencia_percentual = Column(Float, nullable=False)
    distancia_media_foco_zona_metros = Column(Float, nullable=True)
    
    executada_em = Column(DateTime, default=datetime.utcnow)

    analise = relationship("AnaliseRisco", back_populates="validacoes")

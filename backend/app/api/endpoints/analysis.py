"""
Endpoints de processamento e consulta de análises de risco de incêndio florestal.
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import AreaInteresse, AnaliseRisco, IndiceEspectral
from backend.app.schemas.schemas import (
    ProcessarAnaliseRequest,
    AnaliseRiscoResponse,
    AnaliseRiscoDetailResponse
)
from backend.app.services.gee_service import extrair_dados_satelite

router = APIRouter(prefix="/analysis", tags=["Processamento e Análise de Risco"])


@router.post("/process", response_model=AnaliseRiscoDetailResponse)
def processar_analise(requisicao: ProcessarAnaliseRequest, db: Session = Depends(get_db)):
    """
    Executa a pipeline de análise:
    1. Busca os limites geográficos da AOI selecionada.
    2. Adquire reflectâncias orbitais (Sentinel-2 via GEE ou fallback de alta fidelidade).
    3. Calcula os 4 índices espectrais (NDVI, NBR, NDII, PSRI).
    4. Classifica as zonas de risco e consolida as métricas.
    5. Persiste tudo no SQLite e retorna os resultados detalhados.
    """
    area = db.query(AreaInteresse).filter(AreaInteresse.id == requisicao.area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Área de Interesse não encontrada.")

    # Ingestão de dados orbitais e cálculo de índices
    celulas = extrair_dados_satelite(
        min_lat=area.min_lat,
        max_lat=area.max_lat,
        min_lon=area.min_lon,
        max_lon=area.max_lon,
        data_inicio=requisicao.data_inicio,
        data_fim=requisicao.data_fim,
        passo_grade=8
    )

    if not celulas:
        raise HTTPException(status_code=400, detail="Não foram obtidos dados espectrais para o período e área.")

    # Estatísticas consolidadas
    total_celulas = len(celulas)
    celulas_alto_risco = sum(1 for c in celulas if c["nivel_risco"] in ["Alto", "Crítico"])
    media_pontuacao = sum(c["pontuacao_risco"] for c in celulas) / total_celulas

    if media_pontuacao >= 70.0:
        classificacao_geral = "Crítico"
    elif media_pontuacao >= 50.0:
        classificacao_geral = "Alto"
    elif media_pontuacao >= 30.0:
        classificacao_geral = "Moderado"
    else:
        classificacao_geral = "Baixo"

    # Persistência da Análise
    nova_analise = AnaliseRisco(
        area_id=area.id,
        data_referencia=datetime.combine(requisicao.data_fim, datetime.min.time()),
        satelite=requisicao.satelite,
        id_cena_satelite=f"S2_MSI_L2A_{requisicao.data_fim.strftime('%Y%m%d')}",
        classificacao_geral=classificacao_geral,
        pontuacao_risco_media=round(media_pontuacao, 2),
        total_celulas=total_celulas,
        celulas_alto_risco=celulas_alto_risco,
        processada_em=datetime.utcnow()
    )
    db.add(nova_analise)
    db.commit()
    db.refresh(nova_analise)

    # Persistência de cada célula geográfica com seus 4 índices
    for c in celulas:
        reg_indice = IndiceEspectral(
            analise_id=nova_analise.id,
            latitude=c["latitude"],
            longitude=c["longitude"],
            ndvi=c["ndvi"],
            nbr=c["nbr"],
            ndii=c["ndii"],
            psri=c["psri"],
            nivel_risco=c["nivel_risco"],
            pontuacao_risco=c["pontuacao_risco"],
            justificativa=c["justificativa"]
        )
        db.add(reg_indice)

    db.commit()
    db.refresh(nova_analise)
    return nova_analise


@router.get("/history", response_model=List[AnaliseRiscoResponse])
def listar_historico_analises(db: Session = Depends(get_db)):
    """
    Retorna o histórico cronológico de análises de risco salvas no banco de dados.
    """
    return db.query(AnaliseRisco).order_by(AnaliseRisco.processada_em.desc()).all()


@router.get("/{analise_id}", response_model=AnaliseRiscoDetailResponse)
def obter_detalhes_analise(analise_id: int, db: Session = Depends(get_db)):
    """
    Retorna uma análise completa com todas as suas células, índices e coordenadas geográficas.
    """
    analise = db.query(AnaliseRisco).filter(AnaliseRisco.id == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return analise

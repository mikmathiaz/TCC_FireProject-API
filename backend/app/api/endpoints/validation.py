"""
Endpoints para validação cruzada com os dados do BDQueimadas/INPE.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import FocoINPE, ValidacaoCruzada
from backend.app.schemas.schemas import FocoINPEResponse, ValidacaoCruzadaResponse
from backend.app.services.inpe_service import executar_validacao_cruzada, carregar_csv_bdqueimadas
from backend.app.core.config import BASE_DIR

router = APIRouter(prefix="/validation", tags=["Validação Cruzada (INPE)"])


@router.post("/inpe/load-default-sample")
def carregar_amostra_padrao(db: Session = Depends(get_db)):
    """
    Carrega o arquivo CSV de amostra de focos do BDQueimadas para o banco SQLite.
    """
    caminho_csv = BASE_DIR / "data" / "sample_inpe" / "focos_inpe_brasilia_amostra.csv"
    if not caminho_csv.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Arquivo de amostra não encontrado em {caminho_csv}."
        )

    qtd = carregar_csv_bdqueimadas(str(caminho_csv), db)
    return {"status": "sucesso", "registros_importados": qtd}


@router.post("/inpe/cross-validate/{analise_id}", response_model=ValidacaoCruzadaResponse)
def validar_analise(
    analise_id: int,
    raio_tolerancia_metros: float = Query(1000.0, description="Raio de tolerância em metros para acerto"),
    db: Session = Depends(get_db)
):
    """
    Executa a validação cruzada entre a análise selecionada e os focos de calor do INPE.
    """
    try:
        resultado = executar_validacao_cruzada(
            analise_id=analise_id,
            db=db,
            raio_tolerancia_metros=raio_tolerancia_metros
        )
        validacao = db.query(ValidacaoCruzada).filter(
            ValidacaoCruzada.id == resultado["validacao_id"]
        ).first()
        return validacao
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/inpe/focos", response_model=List[FocoINPEResponse])
def listar_focos_inpe(
    limite: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Lista os focos de calor do INPE registrados no banco de dados.
    """
    return db.query(FocoINPE).order_by(FocoINPE.data_hora.desc()).limit(limite).all()


@router.get("/history", response_model=List[ValidacaoCruzadaResponse])
def listar_historico_validacoes(db: Session = Depends(get_db)):
    """
    Lista o histórico de relatórios de validação cruzada gerados.
    """
    return db.query(ValidacaoCruzada).order_by(ValidacaoCruzada.executada_em.desc()).all()

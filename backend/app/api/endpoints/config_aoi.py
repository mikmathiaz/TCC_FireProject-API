"""
Endpoints para gerenciamento de Áreas de Interesse (AOI).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import AreaInteresse
from backend.app.schemas.schemas import AreaInteresseCreate, AreaInteresseResponse

router = APIRouter(prefix="/aoi", tags=["Áreas de Interesse (AOI)"])


@router.get("/", response_model=List[AreaInteresseResponse])
def listar_areas(db: Session = Depends(get_db)):
    """
    Retorna todas as Áreas de Interesse cadastradas.
    Se nenhuma existir, inicializa automaticamente com o Parque Nacional de Brasília.
    """
    areas = db.query(AreaInteresse).all()
    if not areas:
        area_padrao = AreaInteresse(
            nome="Parque Nacional de Brasília",
            descricao="Unidade de Conservação de proteção integral no Distrito Federal (Cerrado).",
            min_lat=-15.75,
            max_lat=-15.55,
            min_lon=-48.05,
            max_lon=-47.85
        )
        db.add(area_padrao)
        db.commit()
        db.refresh(area_padrao)
        areas = [area_padrao]
    return areas


@router.post("/", response_model=AreaInteresseResponse)
def criar_area(dados: AreaInteresseCreate, db: Session = Depends(get_db)):
    """
    Cadastra uma nova Área de Interesse com suas coordenadas delimitadoras.
    """
    area_existente = db.query(AreaInteresse).filter(AreaInteresse.nome == dados.nome).first()
    if area_existente:
        raise HTTPException(status_code=400, detail="Já existe uma AOI com este nome.")

    nova_area = AreaInteresse(
        nome=dados.nome,
        descricao=dados.descricao,
        min_lat=dados.min_lat,
        max_lat=dados.max_lat,
        min_lon=dados.min_lon,
        max_lon=dados.max_lon,
        geojson_geometry=dados.geojson_geometry
    )
    db.add(nova_area)
    db.commit()
    db.refresh(nova_area)
    return nova_area


@router.get("/{area_id}", response_model=AreaInteresseResponse)
def obter_area(area_id: int, db: Session = Depends(get_db)):
    """
    Recupera os detalhes de uma AOI específica pelo ID.
    """
    area = db.query(AreaInteresse).filter(AreaInteresse.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Área de Interesse não encontrada.")
    return area

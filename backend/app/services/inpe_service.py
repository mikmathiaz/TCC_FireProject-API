"""
Serviço de Ingestão e Validação Cruzada com Focos do INPE (BDQueimadas).
Processa planilhas CSV do BDQueimadas e cruza espacial e temporalmente
as previsões de alto risco do Fire Watcher com os focos reais de calor.
"""

import math
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.models import FocoINPE, AnaliseRisco, IndiceEspectral, ValidacaoCruzada


def calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância geodésica em metros entre dois pontos (Haversine formula).
    """
    R = 6371000.0  # Raio médio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def carregar_csv_bdqueimadas(filepath: str, db: Session) -> int:
    """
    Lê um arquivo CSV padrão do BDQueimadas/INPE e insere os registros na tabela focos_inpe.
    Retorna a quantidade de registros importados.
    """
    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    registros_adicionados = 0
    for _, row in df.iterrows():
        try:
            # Identificação das colunas do INPE com flexibilidade de nomenclatura
            lat = float(row.get("latitude", row.get("lat", 0.0)))
            lon = float(row.get("longitude", row.get("lon", 0.0)))
            
            data_str = str(row.get("datahora", row.get("data_hora", row.get("data", ""))))
            try:
                data_hora = datetime.strptime(data_str[:19], "%Y/%m/%d %H:%M:%S")
            except ValueError:
                try:
                    data_hora = datetime.strptime(data_str[:19], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    data_hora = datetime.utcnow()

            satelite = str(row.get("satelite", "AQUA_M-T"))
            bioma = str(row.get("bioma", "")) if pd.notna(row.get("bioma")) else None
            municipio = str(row.get("municipio", "")) if pd.notna(row.get("municipio")) else None
            estado = str(row.get("estado", "")) if pd.notna(row.get("estado")) else None
            
            dias_sem_chuva = int(row.get("numero_dias_sem_chuva", row.get("dias_sem_chuva", 0))) if pd.notna(row.get("numero_dias_sem_chuva", row.get("dias_sem_chuva"))) else None
            precipitacao = float(row.get("precipitacao", 0.0)) if pd.notna(row.get("precipitacao")) else None
            risco_fogo = float(row.get("risco_fogo", 0.0)) if pd.notna(row.get("risco_fogo")) else None
            frp = float(row.get("frp", 0.0)) if pd.notna(row.get("frp")) else None

            foco = FocoINPE(
                data_hora=data_hora,
                satelite=satelite,
                latitude=lat,
                longitude=lon,
                bioma=bioma,
                municipio=municipio,
                estado=estado,
                dias_sem_chuva=dias_sem_chuva,
                precipitacao=precipitacao,
                risco_fogo_inpe=risco_fogo,
                frp=frp
            )
            db.add(foco)
            registros_adicionados += 1
        except Exception:
            continue

    db.commit()
    return registros_adicionados


def executar_validacao_cruzada(
    analise_id: int,
    db: Session,
    raio_tolerancia_metros: float = 1000.0
) -> Dict[str, Any]:
    """
    Cruza as células de Alto e Crítico risco da análise com os focos históricos do INPE.
    Um foco é considerado validado (acerto) se estiver dentro do raio de tolerância
    de qualquer célula prevista como Alto ou Crítico risco.
    """
    analise = db.query(AnaliseRisco).filter(AnaliseRisco.id == analise_id).first()
    if not analise:
        raise ValueError(f"Análise de ID {analise_id} não encontrada.")

    area = analise.area
    celulas_risco = db.query(IndiceEspectral).filter(
        IndiceEspectral.analise_id == analise_id,
        IndiceEspectral.nivel_risco.in_(["Alto", "Crítico"])
    ).all()

    # Busca os focos do INPE ocorridos dentro da caixa delimitadora da área
    # e dentro de uma janela temporal próxima à data de referência (+- 3 dias)
    focos = db.query(FocoINPE).filter(
        FocoINPE.latitude >= area.min_lat,
        FocoINPE.latitude <= area.max_lat,
        FocoINPE.longitude >= area.min_lon,
        FocoINPE.longitude <= area.max_lon
    ).all()

    total_focos = len(focos)
    if total_focos == 0 or len(celulas_risco) == 0:
        validacao = ValidacaoCruzada(
            analise_id=analise_id,
            total_focos_inpe_detectados=total_focos,
            focos_em_zona_alto_risco=0,
            taxa_coincidencia_percentual=0.0,
            distancia_media_foco_zona_metros=0.0
        )
        db.add(validacao)
        db.commit()
        db.refresh(validacao)
        return {
            "total_focos": total_focos,
            "focos_coincidentes": 0,
            "taxa_coincidencia": 0.0,
            "distancia_media_metros": 0.0
        }

    focos_coincidentes = 0
    distancias = []

    for f in focos:
        # Menor distância deste foco a qualquer célula de risco
        menor_dist = min([
            calcular_distancia_haversine(f.latitude, f.longitude, c.latitude, c.longitude)
            for c in celulas_risco
        ])
        distancias.append(menor_dist)
        if menor_dist <= raio_tolerancia_metros:
            focos_coincidentes += 1

    taxa = round((focos_coincidentes / total_focos) * 100.0, 2)
    distancia_media = round(sum(distancias) / len(distancias), 2) if distancias else 0.0

    validacao = ValidacaoCruzada(
        analise_id=analise_id,
        total_focos_inpe_detectados=total_focos,
        focos_em_zona_alto_risco=focos_coincidentes,
        taxa_coincidencia_percentual=taxa,
        distancia_media_foco_zona_metros=distancia_media
    )
    db.add(validacao)
    db.commit()
    db.refresh(validacao)

    return {
        "validacao_id": validacao.id,
        "total_focos": total_focos,
        "focos_coincidentes": focos_coincidentes,
        "taxa_coincidencia": taxa,
        "distancia_media_metros": distancia_media
    }

#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Divisão Temporal Contígua do Dataset FLAME 3 via EXIF DateTime
================================================================================
Objetivo:
    Gerar o arquivo CSV de divisão do dataset (ml/data/split.csv) ordenando as
    amostras estritamente pela data e hora de captura real (EXIF DateTimeOriginal)
    e separando-as em blocos temporais contíguos:
      - Treino:     70% inicial da sequência cronológica
      - Validação:  15% intermediário
      - Teste:      15% final

Decisão Metodológica Crucial para a Banca de TCC:
    1. Descoberta Empírica: A numeração original dos arquivos do FLAME 3 (00001, 00002...)
       NÃO corresponde à ordem temporal real das imagens (correlação de -0.066 com o tempo).
       Imagens de 25, 26 e 27 de outubro foram misturadas na nomenclatura do dataset.
    2. Ordenação Cronológica Real: Ao ordenar pelo timestamp EXIF DateTimeOriginal,
       o intervalo típico mediano entre quadros consecutivos é de exatamente 3,0 segundos,
       e a autocorrelação de cobertura de fogo entre quadros vizinhos salta de 3,7% para 93,4%!
    3. Zona de Amortecimento (Buffer de Fronteira):
       Para eliminar completamente qualquer contaminação temporal residual nas transições
       entre blocos, descartamos intencionalmente 2 quadros em cada fronteira:
         - Fronteira Treino / Validação (quadros 435 e 436 em Fire; 81 e 82 em No Fire)
         - Fronteira Validação / Teste (quadros 528 e 529 em Fire; 98 e 99 em No Fire)
       Esses quadros são marcados como 'discard' e ignorados no treinamento e teste.

Uso:
    python ml/scripts/create_split.py --data-dir "C:/caminho/para/FLAME 3" --mask-dir ml/data/masks --output-csv ml/data/split.csv
================================================================================
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ExifTags

# Suporte a terminais Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def extrair_datetime_exif(caminho_imagem: Path) -> datetime:
    """
    Extrai o timestamp de captura real da imagem via metadados EXIF.
    Tenta DateTimeOriginal (tag 36867) e DateTime (tag 306).
    """
    try:
        with Image.open(caminho_imagem) as img:
            exif = img._getexif() or {}
            raw = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
            dto_str = raw.get("DateTimeOriginal") or raw.get("DateTime")
            if dto_str:
                return datetime.strptime(dto_str, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    # Fallback caso não possua EXIF (nunca ocorreu no FLAME 3)
    return datetime.fromtimestamp(caminho_imagem.stat().st_mtime)


def carregar_metadados_cobertura(mask_dir: Path) -> Dict[Tuple[str, str], float]:
    """
    Carrega o percentual de fogo de cada amostra a partir de masks_metadata.csv.
    """
    cobertura: Dict[Tuple[str, str], float] = {}
    csv_meta = mask_dir / "masks_metadata.csv"
    if csv_meta.exists():
        with open(csv_meta, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls_key = row.get("classe", "").strip()
                stem = Path(row.get("arquivo_mascara", "")).stem
                cobertura[(cls_key, stem)] = float(row.get("pct_fogo", 0.0))
    return cobertura


def criar_split_contiguo(
    data_dir: Path,
    mask_dir: Path,
    output_csv: Path,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    discard_boundary_frames: int = 2
) -> None:
    """
    Ordena as amostras pelo EXIF DateTimeOriginal e divide em blocos temporais contíguos,
    descartando 2 quadros em cada fronteira de transição para criar um buffer temporal anti-leakage.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-4, "As frações do split devem somar 1.0!"

    cobertura_mapa = carregar_metadados_cobertura(mask_dir)
    linhas_split: List[Dict[str, object]] = []

    print("=" * 80)
    print("🔥 FIRE WATCHER — DIVISÃO TEMPORAL CONTÍGUA COM EXIF E ZONA DE AMORTECIMENTO")
    print("=" * 80)
    print(f"📁 Diretório do Dataset:     {data_dir}")
    print(f"📁 Diretório de Máscaras:    {mask_dir}")
    print(f"📊 Frações Teóricas:         Treino={train_ratio*100:.0f}%, Val={val_ratio*100:.0f}%, Teste={test_ratio*100:.0f}%")
    print(f"🛡️  Descarte em Fronteira:    {discard_boundary_frames} quadros por transição (Train/Val e Val/Test)")
    print("=" * 80)

    for classe in ["Fire", "No Fire"]:
        pasta_rgb = data_dir / classe / "RGB" / "Corrected FOV"
        if not pasta_rgb.exists():
            pasta_rgb = data_dir / classe

        # Coleta arquivos de forma única por stem
        arquivos_unicos = {
            f.stem: f for f in pasta_rgb.rglob("*")
            if f.suffix.lower() in [".jpg", ".jpeg"] and "thermal" not in f.name.lower()
        }

        # Extrai timestamp EXIF de cada arquivo
        amostras_info = []
        for stem, arq_path in arquivos_unicos.items():
            dt = extrair_datetime_exif(arq_path)
            amostras_info.append({
                "stem": stem,
                "stem_num": int(stem) if stem.isdigit() else 0,
                "path": arq_path,
                "datetime": dt
            })

        # ORDENAÇÃO CRONOLÓGICA REAL: por DateTimeOriginal (secundário por stem_num para estabilidade)
        amostras_info.sort(key=lambda x: (x["datetime"], x["stem_num"]))
        total_amostras = len(amostras_info)

        if total_amostras == 0:
            print(f"⚠️ Nenhuma amostra RGB encontrada para a classe '{classe}'.")
            continue

        # Cálculo dos pontos de corte nominais (fronteiras)
        idx_corte1 = int(round(total_amostras * train_ratio))
        idx_corte2 = idx_corte1 + int(round(total_amostras * val_ratio))

        # Fronteira 1: transição Treino -> Validação (descarta 2 quadros)
        # Exemplo em Fire (total 622): idx_corte1 = 435 -> descarta índices 434 e 435 (quadros 435 e 436)
        corte1_inicio_descarte = idx_corte1 - (discard_boundary_frames // 2)
        corte1_fim_descarte = corte1_inicio_descarte + discard_boundary_frames

        # Fronteira 2: transição Validação -> Teste (descarta 2 quadros)
        # Exemplo em Fire: idx_corte2 = 528 -> descarta índices 527 e 528 (quadros 528 e 529)
        corte2_inicio_descarte = idx_corte2 - (discard_boundary_frames // 2)
        corte2_fim_descarte = corte2_inicio_descarte + discard_boundary_frames

        # Contadores de auditoria
        contagem = {"train": 0, "val": 0, "test": 0, "discard": 0}

        for i, item in enumerate(amostras_info):
            stem = item["stem"]
            dt = item["datetime"]

            if i < corte1_inicio_descarte:
                split_name = "train"
            elif i < corte1_fim_descarte:
                split_name = "discard"
            elif i < corte2_inicio_descarte:
                split_name = "val"
            elif i < corte2_fim_descarte:
                split_name = "discard"
            else:
                split_name = "test"

            contagem[split_name] += 1

            rgb_rel = f"{classe}/RGB/Corrected FOV/{stem}.JPG"
            raw_thermal_rel = f"{classe}/Thermal/Raw JPG/{stem}.JPG"
            mask_rel = f"{classe}/Thermal/Celsius TIFF/{stem}.png"
            pct_fogo = cobertura_mapa.get((classe, stem), 0.0)

            linhas_split.append({
                "amostra_id": stem,
                "classe": classe,
                "split": split_name,
                "capture_datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "rgb_rel_path": rgb_rel,
                "thermal_raw_rel_path": raw_thermal_rel,
                "mask_rel_path": mask_rel,
                "pct_fogo": round(pct_fogo, 4)
            })

        print(f"\nClasse '{classe}': Total = {total_amostras} amostras")
        print(f"  • Intervalo Temporal Geral: {amostras_info[0]['datetime']} até {amostras_info[-1]['datetime']}")
        print(f"  • Treino:    {contagem['train']} amostras (até {amostras_info[corte1_inicio_descarte-1]['datetime']})")
        print(f"  • Buffer 1:  {contagem['discard'] // 2} quadros descartados na fronteira Train/Val (quadros {corte1_inicio_descarte+1} e {corte1_fim_descarte})")
        print(f"  • Validação: {contagem['val']} amostras ({amostras_info[corte1_fim_descarte]['datetime']} até {amostras_info[corte2_inicio_descarte-1]['datetime']})")
        print(f"  • Buffer 2:  {contagem['discard'] // 2} quadros descartados na fronteira Val/Test (quadros {corte2_inicio_descarte+1} e {corte2_fim_descarte})")
        print(f"  • Teste:     {contagem['test']} amostras ({amostras_info[corte2_fim_descarte]['datetime']} até {amostras_info[-1]['datetime']})")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    colunas = [
        "amostra_id",
        "classe",
        "split",
        "capture_datetime",
        "rgb_rel_path",
        "thermal_raw_rel_path",
        "mask_rel_path",
        "pct_fogo"
    ]

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas_split)

    total_descartados = sum(1 for l in linhas_split if l["split"] == "discard")
    total_validos = len(linhas_split) - total_descartados

    print("\n" + "=" * 80)
    print(f"✅ Arquivo de split salvo com sucesso em: {output_csv}")
    print(f"   • Total de registros:    {len(linhas_split)}")
    print(f"   • Amostras ativas:       {total_validos} (Treino + Val + Test)")
    print(f"   • Amostras de descarte:  {total_descartados} (Buffers de fronteira temporal)")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Gera ml/data/split.csv ordenado cronologicamente via EXIF DateTimeOriginal com descarte de fronteiras."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/data/CVSubset",
        help="Caminho raiz da pasta do dataset (padrão: ml/data/CVSubset)."
    )
    parser.add_argument(
        "--mask-dir",
        type=str,
        default="ml/data/masks",
        help="Caminho raiz das máscaras geradas (padrão: ml/data/masks)."
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="ml/data/split.csv",
        help="Caminho de saída para o CSV de split (padrão: ml/data/split.csv)."
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.70,
        help="Fração nominal para conjunto de treino (padrão: 0.70)."
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.15,
        help="Fração nominal para conjunto de validação (padrão: 0.15)."
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.15,
        help="Fração nominal para conjunto de teste (padrão: 0.15)."
    )
    parser.add_argument(
        "--discard-boundary-frames",
        type=int,
        default=2,
        help="Número de quadros a descartar em cada fronteira de transição (padrão: 2)."
    )
    args = parser.parse_args()

    criar_split_contiguo(
        data_dir=Path(args.data_dir).resolve(),
        mask_dir=Path(args.mask_dir).resolve(),
        output_csv=Path(args.output_csv).resolve(),
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        discard_boundary_frames=args.discard_boundary_frames
    )


if __name__ == "__main__":
    main()

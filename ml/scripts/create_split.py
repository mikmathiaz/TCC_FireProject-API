#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Divisão Temporal Contígua do Dataset FLAME 3 (Train / Val / Test)
================================================================================
Objetivo:
    Gerar o arquivo CSV de divisão do dataset (ml/data/split.csv) separando
    as amostras em blocos temporais contíguos:
      - Treino:     70% inicial da sequência cronológica
      - Validação:  15% intermediário
      - Teste:      15% final

Decisão Metodológica para a Banca de TCC:
    - Quadros consecutivos gravados por drone em voo apresentam forte correlação
      espacial e temporal (quadros adjacentes diferem por milissegundos).
    - Um split aleatório tradicional (random split) causaria vazamento massivo
      de dados (data leakage), inflando artificialmente as métricas de IoU e F1.
    - A divisão em blocos cronológicos contíguos garante que os conjuntos de validação
      e teste simulem o comportamento real em produção: predição em momentos
      futuros do voo ainda não vistos pelo modelo.

Uso:
    python ml/scripts/create_split.py --data-dir "C:/caminho/para/FLAME 3" --mask-dir ml/data/masks --output-csv ml/data/split.csv
================================================================================
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Suporte a terminais Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


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
    test_ratio: float = 0.15
) -> None:
    """
    Divide ordenadamente as sequências cronológicas de Fire e No Fire em blocos contíguos.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-4, "As frações do split devem somar 1.0!"

    cobertura_mapa = carregar_metadados_cobertura(mask_dir)
    linhas_split: List[Dict[str, object]] = []

    print("=" * 80)
    print("🔥 FIRE WATCHER — GERAÇÃO DO SPLIT TEMPORAL CONTÍGUO (FLAME 3)")
    print("=" * 80)
    print(f"📁 Diretório do Dataset:  {data_dir}")
    print(f"📁 Diretório de Máscaras: {mask_dir}")
    print(f"📊 Proporções:            Treino={train_ratio*100:.0f}%, Val={val_ratio*100:.0f}%, Teste={test_ratio*100:.0f}%")
    print("=" * 80)

    for classe in ["Fire", "No Fire"]:
        # Busca todas as amostras disponíveis de forma ordenada
        pasta_rgb = data_dir / classe / "RGB" / "Corrected FOV"
        pasta_raw = data_dir / classe / "Thermal" / "Raw JPG"
        pasta_mask = mask_dir / classe / "Thermal" / "Celsius TIFF"

        if not pasta_rgb.exists():
            # Fallback para estrutura sem subpastas canônicas
            pasta_rgb = data_dir / classe

        # Coleta arquivos e mapeia por stem
        arquivos_rgb = sorted(list({f.stem: f for f in pasta_rgb.rglob("*") if f.suffix.lower() in [".jpg", ".jpeg"] and "thermal" not in f.name.lower()}.values()), key=lambda x: x.stem)
        total_amostras = len(arquivos_rgb)

        if total_amostras == 0:
            print(f"⚠️ Nenhuma amostra RGB encontrada para a classe '{classe}'.")
            continue

        n_train = int(round(total_amostras * train_ratio))
        n_val = int(round(total_amostras * val_ratio))
        # O restante vai para teste
        n_test = total_amostras - (n_train + n_val)

        print(f"\nClasse '{classe}': Total = {total_amostras} amostras")
        print(f"  • Treino:    {n_train} amostras (00001 a {arquivos_rgb[n_train-1].stem})")
        print(f"  • Validação: {n_val} amostras ({arquivos_rgb[n_train].stem} a {arquivos_rgb[n_train+n_val-1].stem})")
        print(f"  • Teste:     {n_test} amostras ({arquivos_rgb[n_train+n_val].stem} a {arquivos_rgb[-1].stem})")

        for i, arq_rgb in enumerate(arquivos_rgb):
            stem = arq_rgb.stem

            if i < n_train:
                split_name = "train"
            elif i < (n_train + n_val):
                split_name = "val"
            else:
                split_name = "test"

            # Caminhos relativos padrão no bundle / dataset
            rgb_rel = f"{classe}/RGB/Corrected FOV/{stem}.JPG"
            raw_thermal_rel = f"{classe}/Thermal/Raw JPG/{stem}.JPG"
            mask_rel = f"{classe}/Thermal/Celsius TIFF/{stem}.png"

            pct_fogo = cobertura_mapa.get((classe, stem), 0.0)

            linhas_split.append({
                "amostra_id": stem,
                "classe": classe,
                "split": split_name,
                "rgb_rel_path": rgb_rel,
                "thermal_raw_rel_path": raw_thermal_rel,
                "mask_rel_path": mask_rel,
                "pct_fogo": round(pct_fogo, 4)
            })

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    colunas = [
        "amostra_id",
        "classe",
        "split",
        "rgb_rel_path",
        "thermal_raw_rel_path",
        "mask_rel_path",
        "pct_fogo"
    ]

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas_split)

    print("\n" + "=" * 80)
    print(f"✅ Arquivo de split salvo com sucesso em: {output_csv}")
    print(f"   Total de registros gerados: {len(linhas_split)}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Gera ml/data/split.csv dividindo o FLAME 3 em blocos temporais contíguos."
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
        help="Fração para conjunto de treino (padrão: 0.70)."
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.15,
        help="Fração para conjunto de validação (padrão: 0.15)."
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.15,
        help="Fração para conjunto de teste (padrão: 0.15)."
    )
    args = parser.parse_args()

    criar_split_contiguo(
        data_dir=Path(args.data_dir).resolve(),
        mask_dir=Path(args.mask_dir).resolve(),
        output_csv=Path(args.output_csv).resolve(),
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )


if __name__ == "__main__":
    main()

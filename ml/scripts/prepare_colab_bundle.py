#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Preparação do Pacote Compacto para Google Colab (Bundle .ZIP)
================================================================================
Objetivo:
    Gerar um único arquivo comprimido (.zip) contendo ESTRITAMENTE os arquivos
    necessários para o treinamento das modalidades 'rgb' e 'thermal' no Google Colab:
      1. RGB com Campo de Visão Corrigido (Fire e No Fire: 738 imagens 640x512)
      2. Térmico em Paleta Original (Raw JPG: 738 imagens 640x512)
      3. Máscaras Binárias de Fogo (738 máscaras PNG 640x512)
      4. Arquivo de Divisão Temporal (ml/data/split.csv)

Benefício Prático:
    - O dataset bruto original (CVSubset.zip) possui 6,23 GB devido às fotos
      RGB de 4000x3000 e aos TIFFs radiométricos pesados.
    - Este bundle compacto exclui o que não é usado no treino, reduzindo o tamanho
      total para aproximadamente ~150-250 MB, tornando o upload para o Google Drive
      e a descompactação no Colab extremamente rápidos (menos de 1 minuto).

Uso:
    python ml/scripts/prepare_colab_bundle.py --data-dir "C:/caminho/para/FLAME 3" --mask-dir ml/data/masks --split-csv ml/data/split.csv --output-zip ml/data/flame3_colab_bundle.zip
================================================================================
"""

import argparse
import sys
import zipfile
from pathlib import Path
from typing import List, Tuple

# Suporte a terminais Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def criar_bundle_colab(
    data_dir: Path,
    mask_dir: Path,
    split_csv: Path,
    output_zip: Path
) -> None:
    """
    Empacota imagens selecionadas, máscaras e split.csv em um único .zip.
    """
    if not split_csv.exists():
        print(f"❌ ERRO: O arquivo '{split_csv}' não existe. Execute primeiro 'create_split.py'.")
        sys.exit(1)

    output_zip.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("📦 FIRE WATCHER — EMPACOTAMENTO DO DATASET PARA O GOOGLE COLAB")
    print("=" * 80)
    print(f"📁 Diretório Dataset:   {data_dir}")
    print(f"📁 Diretório Máscaras:  {mask_dir}")
    print(f"📄 Arquivo Split:       {split_csv}")
    print(f"💾 Arquivo ZIP Destino: {output_zip}")
    print("=" * 80)

    arquivos_para_incluir: List[Tuple[Path, str]] = []

    # 1. Adicionar split.csv na raiz do bundle
    arquivos_para_incluir.append((split_csv, "split.csv"))

    # 2. Adicionar masks_metadata.csv se existir
    csv_meta = mask_dir / "masks_metadata.csv"
    if csv_meta.exists():
        arquivos_para_incluir.append((csv_meta, "masks_metadata.csv"))

    # 3. Coletar imagens RGB Corrigido e Thermal Raw JPG para Fire e No Fire
    total_rgb = 0
    total_raw = 0
    total_masks = 0

    for classe in ["Fire", "No Fire"]:
        # (a) RGB Corrected FOV
        pasta_rgb = data_dir / classe / "RGB" / "Corrected FOV"
        if pasta_rgb.exists():
            for f in sorted(pasta_rgb.glob("*")):
                if f.suffix.lower() in [".jpg", ".jpeg", ".png"] and not f.name.startswith("."):
                    arcname = f"{classe}/RGB/Corrected FOV/{f.name}"
                    arquivos_para_incluir.append((f, arcname))
                    total_rgb += 1

        # (b) Thermal Raw JPG
        pasta_raw = data_dir / classe / "Thermal" / "Raw JPG"
        if pasta_raw.exists():
            for f in sorted(pasta_raw.glob("*")):
                if f.suffix.lower() in [".jpg", ".jpeg", ".png"] and not f.name.startswith("."):
                    arcname = f"{classe}/Thermal/Raw JPG/{f.name}"
                    arquivos_para_incluir.append((f, arcname))
                    total_raw += 1

        # (c) Máscaras PNG
        pasta_mask_cls = mask_dir / classe
        if pasta_mask_cls.exists():
            for f in sorted(pasta_mask_cls.rglob("*.png")):
                if not f.name.startswith("."):
                    # Espelha caminho da máscara dentro de masks/
                    rel_p = f.relative_to(mask_dir)
                    arcname = f"masks/{rel_p.as_posix()}"
                    arquivos_para_incluir.append((f, arcname))
                    total_masks += 1

    print("\n🔍 CONTAGEM DE ARQUIVOS MAPEADOS:")
    print(f"  • Imagens RGB Corrigido:  {total_rgb}")
    print(f"  • Imagens Térmicas Raw:   {total_raw}")
    print(f"  • Máscaras Binárias PNG:  {total_masks}")
    print(f"  • Arquivos de Config/CSV: 2 (split.csv, masks_metadata.csv)")
    print(f"  • Total Geral de Itens:   {len(arquivos_para_incluir)}")

    if len(arquivos_para_incluir) <= 2:
        print("\n❌ ERRO: Nenhuma imagem ou máscara foi encontrada para empacotar.")
        print("Verifique os caminhos passados em --data-dir e --mask-dir.")
        sys.exit(1)

    print(f"\n📦 Gravando arquivo compactado em '{output_zip}' (compressão ZIP_DEFLATED)...")

    # Escrita do arquivo ZIP com compressão padrão
    with zipfile.ZipFile(output_zip, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for idx, (caminho_real, arcname) in enumerate(arquivos_para_incluir, 1):
            if idx % 200 == 0 or idx == len(arquivos_para_incluir):
                print(f"   [{idx}/{len(arquivos_para_incluir)}] arquivos compactados...")
            zipf.write(caminho_real, arcname=arcname)

    tamanho_mb = output_zip.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 80)
    print("🏁 PACOTE COLAB GERADO COM SUCESSO!")
    print("=" * 80)
    print(f"  • Arquivo:    {output_zip.name}")
    print(f"  • Localização: {output_zip.resolve()}")
    print(f"  • Tamanho:    {tamanho_mb:.2f} MB")
    print("\n📌 PRÓXIMO PASSO:")
    print("  1. Faça upload deste arquivo .zip para uma pasta do seu Google Drive")
    print("     (exemplo: 'Meu Drive/TCC_FireWatcher/flame3_colab_bundle.zip').")
    print("  2. Abra o notebook 'ml/notebooks/colab_train.ipynb' no Google Colab com GPU.")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Gera um único .zip compacto para treino no Google Colab (RGB + Raw JPG + Máscaras + Split)."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/data/CVSubset",
        help="Caminho raiz do dataset extraído (padrão: ml/data/CVSubset)."
    )
    parser.add_argument(
        "--mask-dir",
        type=str,
        default="ml/data/masks",
        help="Caminho raiz das máscaras geradas (padrão: ml/data/masks)."
    )
    parser.add_argument(
        "--split-csv",
        type=str,
        default="ml/data/split.csv",
        help="Caminho para o split.csv (padrão: ml/data/split.csv)."
    )
    parser.add_argument(
        "--output-zip",
        type=str,
        default="ml/data/flame3_colab_bundle.zip",
        help="Caminho do arquivo .zip final gerado (padrão: ml/data/flame3_colab_bundle.zip)."
    )
    args = parser.parse_args()

    criar_bundle_colab(
        data_dir=Path(args.data_dir).resolve(),
        mask_dir=Path(args.mask_dir).resolve(),
        split_csv=Path(args.split_csv).resolve(),
        output_zip=Path(args.output_zip).resolve()
    )


if __name__ == "__main__":
    main()

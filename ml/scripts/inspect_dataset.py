#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Inspeção e Diagnóstico do Dataset FLAME 3 (CVSubset)
================================================================================
Objetivo:
    Percorrer a pasta do dataset FLAME 3 (Sycan Marsh, drone DJI M30T),
    exibir a árvore de diretórios, contabilizar amostras por classe
    ("Fire" e "No Fire") e inspecionar os arquivos térmicos radiométricos (.TIFF),
    extraindo dimensões, tipos de dados e estatísticas de temperatura em °C.

Motivação Acadêmica / Defesa de TCC:
    - O sensor radiométrico do drone DJI M30T grava matrizes de temperatura absoluta
      em graus Celsius em formato TIFF de ponto flutuante (ou inteiros escalonados).
    - O dataset não fornece anotações manuais de segmentação (ground truth).
      A verdade de solo será gerada aplicando um limiar térmico físico (ex: >= 80 °C).
    - Esta inspeção prévia valida se as temperaturas máximas e mínimas estão
      na escala esperada e quantifica o percentual inicial de pixels de fogo,
      comprovando o forte desbalanceamento de classes (fogo é minoria dos pixels).

Uso:
    python ml/scripts/inspect_dataset.py --data-dir ml/data/CVSubset --threshold 80.0
================================================================================
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np

# Tentativa de importação de leitor de TIFF com fallback gracioso:
# 1. 'tifffile': padrão da comunidade científica para TIFFs radiométricos float32
# 2. 'PIL.Image': biblioteca padrão de imagens já presente no ambiente
try:
    import tifffile
    HAS_TIFFFILE = True
except ImportError:
    tifffile = None
    HAS_TIFFFILE = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    Image = None
    HAS_PIL = False


def carregar_tiff_temperatura(caminho_tiff: Path) -> np.ndarray:
    """
    Carrega o arquivo TIFF térmico retornando a matriz NumPy 2D de temperaturas em °C.
    
    Decisão de Implementação:
        Dá preferência ao `tifffile` por ler metadados radiométricos e ponto
        flutuante de 32 bits sem risco de quantização. Se ausente, usa `PIL.Image`.
    """
    if HAS_TIFFFILE:
        matriz = tifffile.imread(str(caminho_tiff))
    elif HAS_PIL:
        img = Image.open(str(caminho_tiff))
        matriz = np.array(img)
    else:
        raise RuntimeError(
            "Nenhuma biblioteca para leitura de TIFF disponível. "
            "Instale 'tifffile' ou 'Pillow' (pip install tifffile Pillow)."
        )

    # Se a matriz possuir canal singleton (ex: (1, 512, 640) ou (512, 640, 1)), remove
    if matriz.ndim == 3 and matriz.shape[0] == 1:
        matriz = matriz[0]
    elif matriz.ndim == 3 and matriz.shape[-1] == 1:
        matriz = matriz[:, :, 0]

    return matriz.astype(np.float32)


def imprimir_arvore_diretorios(diretorio_raiz: Path, nivel_maximo: int = 3, prefixo: str = "") -> None:
    """
    Imprime de forma visual a árvore de diretórios até uma profundidade configurável.
    """
    if nivel_maximo < 0:
        return

    itens = sorted([item for item in diretorio_raiz.iterdir() if not item.name.startswith(".")])
    dirs = [item for item in itens if item.is_dir()]
    arquivos = [item for item in itens if item.is_file()]

    # Contagem de arquivos por extensão neste nível
    contagem_ext: Dict[str, int] = {}
    for arq in arquivos:
        ext = arq.suffix.lower() or "(sem extensão)"
        contagem_ext[ext] = contagem_ext.get(ext, 0) + 1

    if contagem_ext:
        resumo_arquivos = ", ".join([f"{qtd} {ext}" for ext, qtd in sorted(contagem_ext.items())])
        print(f"{prefixo}└── 📄 [{resumo_arquivos}]")

    for i, sub_dir in enumerate(dirs):
        eh_ultimo = (i == len(dirs) - 1)
        simbolo = "└── " if eh_ultimo else "├── "
        print(f"{prefixo}{simbolo}📁 {sub_dir.name}/")
        proximo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
        imprimir_arvore_diretorios(sub_dir, nivel_maximo - 1, proximo_prefixo)


def classificar_caminho_classe(caminho: Path) -> str:
    """
    Determina a classe da amostra ('Fire' ou 'No Fire') a partir do caminho do arquivo.
    """
    partes = [p.lower().replace("_", " ").strip() for p in caminho.parts]
    if any("no fire" in p or "nofire" in p for p in partes):
        return "No Fire"
    elif any("fire" in p for p in partes):
        return "Fire"
    return "Desconhecido"


def identificar_arquivos_dataset(diretorio_raiz: Path) -> Dict[str, List[Path]]:
    """
    Varre recursivamente o diretório raiz e agrupa os caminhos de arquivos por categoria:
    - thermal_tiff: Arquivos .tif ou .tiff
    - images_jpg: Arquivos .jpg ou .jpeg
    """
    extensoes_tiff = {".tif", ".tiff"}
    extensoes_jpg = {".jpg", ".jpeg"}

    arquivos_tiff: List[Path] = []
    arquivos_jpg: List[Path] = []

    for arq in diretorio_raiz.rglob("*"):
        if not arq.is_file() or arq.name.startswith("."):
            continue
        ext = arq.suffix.lower()
        if ext in extensoes_tiff:
            arquivos_tiff.append(arq)
        elif ext in extensoes_jpg:
            arquivos_jpg.append(arq)

    arquivos_tiff.sort()
    arquivos_jpg.sort()

    return {
        "thermal_tiff": arquivos_tiff,
        "images_jpg": arquivos_jpg
    }


def inspecionar_amostra_tiff(caminho_tiff: Path, limiar_fogo: float) -> Dict[str, object]:
    """
    Lê uma matriz TIFF térmica e extrai métricas físicas e estatísticas.
    """
    matriz = carregar_tiff_temperatura(caminho_tiff)
    total_pixels = matriz.size

    val_min = float(np.nanmin(matriz))
    val_max = float(np.nanmax(matriz))
    val_media = float(np.nanmean(matriz))
    val_mediana = float(np.nanmedian(matriz))

    # Identificação de anomalias
    num_nans = int(np.isnan(matriz).sum())
    num_infs = int(np.isinf(matriz).sum())

    # Segmentação prévia pelo limiar
    pixels_fogo = int(np.sum(matriz >= limiar_fogo))
    pct_fogo = (pixels_fogo / total_pixels) * 100.0

    return {
        "caminho": caminho_tiff,
        "nome": caminho_tiff.name,
        "shape": matriz.shape,
        "dtype": str(matriz.dtype),
        "total_pixels": total_pixels,
        "temp_min": val_min,
        "temp_max": val_max,
        "temp_media": val_media,
        "temp_mediana": val_mediana,
        "num_nans": num_nans,
        "num_infs": num_infs,
        "pixels_fogo": pixels_fogo,
        "pct_fogo": pct_fogo
    }


def main():
    parser = argparse.ArgumentParser(
        description="Inspeciona o dataset FLAME 3 (CVSubset) e exibe diagnósticos estatísticos dos TIFFs térmicos."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/data/CVSubset",
        help="Caminho raiz da pasta do dataset extraído (padrão: ml/data/CVSubset)."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Limiar de temperatura em °C para considerar fogo na inspeção (padrão: 80.0 °C)."
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=3,
        help="Quantidade de amostras TIFF a detalhar por classe (padrão: 3)."
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Profundidade máxima da árvore de diretórios impressa (padrão: 3)."
    )
    args = parser.parse_args()

    caminho_raiz = Path(args.data_dir).resolve()

    print("=" * 80)
    print("🔥 FIRE WATCHER — INSPEÇÃO DO DATASET FLAME 3 (CVSubset)")
    print("=" * 80)
    print(f"📁 Diretório informado: {caminho_raiz}")
    print(f"🌡️  Limiar de teste para fogo: >= {args.threshold:.1f} °C")
    print(f"📦 Backend TIFF ativo: {'tifffile' if HAS_TIFFFILE else 'Pillow (fallback)'}")
    print("=" * 80)

    if not caminho_raiz.exists():
        print(f"\n❌ ERRO: O diretório '{caminho_raiz}' não foi encontrado.")
        print("Por favor, verifique se o CVSubset.zip foi descompactado no caminho correto.")
        print("Exemplo de execução:")
        print("    python ml/scripts/inspect_dataset.py --data-dir /caminho/para/CVSubset\n")
        sys.exit(1)

    # 1. Árvore de Diretórios
    print("\n📂 1. ESTRUTURA DE DIRETÓRIOS:")
    print(f"{caminho_raiz.name}/")
    imprimir_arvore_diretorios(caminho_raiz, nivel_maximo=args.max_depth)

    # 2. Contagem e Agrupamento
    arquivos = identificar_arquivos_dataset(caminho_raiz)
    tiffs = arquivos["thermal_tiff"]
    jpgs = arquivos["images_jpg"]

    print("\n" + "=" * 80)
    print("📊 2. CONTAGEM GERAL DE ARQUIVOS:")
    print(f"  • Total de TIFFs radiométricos (.tif/.tiff): {len(tiffs)}")
    print(f"  • Total de imagens ópticas/térmicas (.jpg):  {len(jpgs)}")
    print(f"  • Total geral de arquivos de mídia:          {len(tiffs) + len(jpgs)}")

    # Separação por classe
    tiffs_por_classe: Dict[str, List[Path]] = {"Fire": [], "No Fire": [], "Desconhecido": []}
    for tiff in tiffs:
        cls = classificar_caminho_classe(tiff)
        tiffs_por_classe[cls].append(tiff)

    jpgs_por_classe: Dict[str, List[Path]] = {"Fire": [], "No Fire": [], "Desconhecido": []}
    for jpg in jpgs:
        cls = classificar_caminho_classe(jpg)
        jpgs_por_classe[cls].append(jpg)

    print("\n📈 3. AMOSTRAS POR CLASSE:")
    for cls in ["Fire", "No Fire", "Desconhecido"]:
        qtd_t = len(tiffs_por_classe[cls])
        qtd_j = len(jpgs_por_classe[cls])
        if qtd_t > 0 or qtd_j > 0:
            print(f"  • Classe '{cls}':")
            print(f"      - TIFFs térmicos: {qtd_t}")
            print(f"      - Imagens JPG:    {qtd_j}")

    if not tiffs:
        print("\n⚠️ AVISO: Nenhum arquivo .tif ou .tiff foi localizado no diretório fornecido.")
        print("Certifique-se de que a pasta aponta para o diretório correto com os TIFFs radiométricos.")
        return

    # 3. Inspeção detalhada de amostras de TIFF
    print("\n" + "=" * 80)
    print(f"🔬 4. INSPEÇÃO DETALHADA DE AMOSTRAS TIFF (Limiar: >= {args.threshold:.1f} °C):")
    print("=" * 80)

    for cls in ["Fire", "No Fire"]:
        amostras_classe = tiffs_por_classe[cls][:args.num_samples]
        if not amostras_classe:
            continue

        print(f"\n--- [Classe: {cls}] (Mostrando {len(amostras_classe)} amostras) ---")
        for i, caminho_amostra in enumerate(amostras_classe, 1):
            try:
                dados = inspecionar_amostra_tiff(caminho_amostra, args.threshold)
                print(f"\n  [{i}] Arquivo: {dados['nome']}")
                print(f"      Caminho: {dados['caminho']}")
                print(f"      Dimensões (Shape):     {dados['shape']} (Altura x Largura)")
                print(f"      Tipo de dado (dtype):  {dados['dtype']}")
                print(f"      Temperatura Mínima:    {dados['temp_min']:.2f} °C")
                print(f"      Temperatura Máxima:    {dados['temp_max']:.2f} °C")
                print(f"      Temperatura Média:     {dados['temp_media']:.2f} °C (Mediana: {dados['temp_mediana']:.2f} °C)")
                print(f"      Pixels >= {args.threshold:.1f} °C:      {dados['pixels_fogo']:,} de {dados['total_pixels']:,} ({dados['pct_fogo']:.2f}%)")
                
                if dados['num_nans'] > 0 or dados['num_infs'] > 0:
                    print(f"      ⚠️ ALERTA: Detectados {dados['num_nans']} NaNs e {dados['num_infs']} Infs nesta matriz!")

            except Exception as e:
                print(f"  [{i}] ❌ Falha ao carregar {caminho_amostra.name}: {e}")

    print("\n" + "=" * 80)
    print("✅ Inspeção concluída com sucesso.")
    print("=" * 80)


if __name__ == "__main__":
    main()

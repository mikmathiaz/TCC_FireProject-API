#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Geração de Máscaras de Segmentação Binária a partir de TIFFs
================================================================================
Objetivo:
    Converter os arquivos radiométricos térmicos (.TIFF) do dataset FLAME 3
    em máscaras de segmentação binária 2D (.PNG), onde pixels com temperatura
    >= limiar parametrizável (padrão: 80.0 °C) são classificados como fogo (255)
    e os demais como fundo/não-fogo (0).

Motivação Científica e Metodológica para o TCC:
    1. O FLAME 3 CVSubset não possui anotações manuais poligonais; o próprio
       artigo dos autores e a literatura de termografia com UAV utilizam a
       temperatura radiométrica calibrada como "verdade de solo física".
    2. Temperaturas iguais ou superiores a 80 °C em vegetação indicam
       inequivocamente combustão ativa ou braseiro intenso (smoldering),
       eliminando ruídos causados por aquecimento solar do solo (que no Cerrado
       ou florestas secas atinge entre 45 °C e 60 °C).
    3. As máscaras são salvas como PNG em escala de cinza de 8 bits (uint8)
       sem perdas (lossless), mantendo rigorosamente a resolução original
       de 640x512 pixels alinhada ao canal RGB corrigido do DJI M30T.
    4. Um arquivo CSV de metadados ('masks_metadata.csv') é gerado automaticamente,
       registrando a área de fogo (pixels e percentual) e extremos de temperatura,
       essencial para a seção de resultados e discussão do TCC.

Uso:
    python ml/scripts/generate_masks.py --data-dir ml/data/CVSubset --output-dir ml/data/masks --threshold 80.0
================================================================================
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

# Suporte prioritário a tifffile com fallback para PIL
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

# Suporte opcional a tqdm para barra de progresso visual
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    tqdm = None
    HAS_TQDM = False


def carregar_tiff_temperatura(caminho_tiff: Path) -> np.ndarray:
    """
    Carrega o arquivo TIFF térmico radiométrico e retorna matriz 2D em float32 (°C).
    """
    if HAS_TIFFFILE:
        matriz = tifffile.imread(str(caminho_tiff))
    elif HAS_PIL:
        img = Image.open(str(caminho_tiff))
        matriz = np.array(img)
    else:
        raise RuntimeError("Instale 'tifffile' ou 'Pillow' para carregar arquivos TIFF.")

    if matriz.ndim == 3 and matriz.shape[0] == 1:
        matriz = matriz[0]
    elif matriz.ndim == 3 and matriz.shape[-1] == 1:
        matriz = matriz[:, :, 0]

    return matriz.astype(np.float32)


def classificar_classe_por_caminho(caminho: Path) -> str:
    """
    Extrai se o arquivo pertence a 'Fire' ou 'No Fire'.
    """
    partes = [p.lower().replace("_", " ").strip() for p in caminho.parts]
    if any("no fire" in p or "nofire" in p for p in partes):
        return "No Fire"
    elif any("fire" in p for p in partes):
        return "Fire"
    return "Desconhecido"


def obter_caminho_saida_mascara(
    caminho_tiff: Path,
    diretorio_origem: Path,
    diretorio_destino: Path
) -> Path:
    """
    Calcula o caminho de saída espelhando a hierarquia de pastas da origem.
    Substitui a extensão (.tif/.tiff) por .png.
    """
    try:
        rel_path = caminho_tiff.relative_to(diretorio_origem)
    except ValueError:
        rel_path = Path(caminho_tiff.name)

    # Altera extensão para .png
    rel_path_png = rel_path.with_suffix(".png")
    caminho_final = diretorio_destino / rel_path_png
    return caminho_final


def processar_mascaras(
    data_dir: Path,
    output_dir: Path,
    threshold: float,
    binary_value: int = 255,
    overwrite: bool = False,
    save_metadata_csv: bool = True
) -> Dict[str, object]:
    """
    Executa a pipeline de conversão de todos os TIFFs em máscaras binárias.
    """
    extensoes_tiff = {".tif", ".tiff"}
    arquivos_tiff = [
        arq for arq in sorted(data_dir.rglob("*"))
        if arq.is_file() and arq.suffix.lower() in extensoes_tiff and not arq.name.startswith(".")
    ]

    total_arquivos = len(arquivos_tiff)
    if total_arquivos == 0:
        print(f"❌ Nenhum arquivo TIFF (.tif / .tiff) encontrado em '{data_dir}'.")
        return {"total_gerados": 0}

    print(f"\n🚀 Iniciando geração de máscaras para {total_arquivos} arquivos TIFF...")
    print(f"   • Limiar adotado: >= {threshold:.1f} °C -> valor {binary_value}")
    print(f"   • Diretório de saída: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    metadados: List[Dict[str, object]] = []
    gerados_count = 0
    pulados_count = 0

    # Iterador com barra de progresso (ou loop simples caso tqdm não esteja instalado)
    iterador = tqdm(arquivos_tiff, desc="Gerando máscaras") if HAS_TQDM else arquivos_tiff

    for idx, caminho_tiff in enumerate(iterador, 1):
        if not HAS_TQDM and (idx % 100 == 0 or idx == total_arquivos):
            print(f"   [{idx}/{total_arquivos}] processados...")

        caminho_saida = obter_caminho_saida_mascara(caminho_tiff, data_dir, output_dir)
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)

        if caminho_saida.exists() and not overwrite:
            pulados_count += 1
            continue

        try:
            matriz_temp = carregar_tiff_temperatura(caminho_tiff)
            
            # Geração da máscara binária
            # Pixels com temperatura >= threshold recebem binary_value (255), demais 0
            mascara = np.zeros(matriz_temp.shape, dtype=np.uint8)
            mascara[matriz_temp >= threshold] = binary_value

            # Salvando como PNG (Modo 'L' para escala de cinza 8-bit sem perdas)
            img_mascara = Image.fromarray(mascara, mode="L")
            img_mascara.save(str(caminho_saida), format="PNG", compress_level=6)

            # Métricas estatísticas da amostra
            classe = classificar_classe_por_caminho(caminho_tiff)
            total_pixels = matriz_temp.size
            pixels_fogo = int(np.sum(mascara == binary_value))
            pct_fogo = (pixels_fogo / total_pixels) * 100.0

            metadados.append({
                "arquivo_tiff": str(caminho_tiff.name),
                "caminho_tiff_rel": str(caminho_tiff.relative_to(data_dir)),
                "arquivo_mascara": str(caminho_saida.name),
                "caminho_mascara_rel": str(caminho_saida.relative_to(output_dir)),
                "classe": classe,
                "shape_h": matriz_temp.shape[0],
                "shape_w": matriz_temp.shape[1],
                "temp_min": round(float(np.nanmin(matriz_temp)), 2),
                "temp_max": round(float(np.nanmax(matriz_temp)), 2),
                "temp_media": round(float(np.nanmean(matriz_temp)), 2),
                "limiar_usado": threshold,
                "pixels_fogo": pixels_fogo,
                "pct_fogo": round(pct_fogo, 4)
            })

            gerados_count += 1

        except Exception as e:
            print(f"\n❌ Erro ao processar '{caminho_tiff.name}': {e}")

    # Salva relatório de metadados em CSV
    if save_metadata_csv and metadados:
        caminho_csv = output_dir / "masks_metadata.csv"
        colunas = list(metadados[0].keys())
        with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=colunas)
            escritor.writeheader()
            escritor.writerows(metadados)
        print(f"\n📊 Relatório consolidado de metadados salvo em: {caminho_csv}")

    # Estatísticas de finalização
    print("\n" + "=" * 80)
    print("🏁 RESUMO DA GERAÇÃO DE MÁSCARAS:")
    print(f"  • Máscaras geradas com sucesso:  {gerados_count}")
    print(f"  • Máscaras ignoradas (já existiam): {pulados_count}")
    print(f"  • Total de TIFFs mapeados:       {total_arquivos}")

    if metadados:
        fogo_por_classe: Dict[str, List[float]] = {}
        for m in metadados:
            cls = str(m["classe"])
            fogo_por_classe.setdefault(cls, []).append(float(m["pct_fogo"]))

        print("\n📈 ESTATÍSTICAS DE COBERTURA DE FOGO:")
        for cls, pcts in fogo_por_classe.items():
            media_pct = sum(pcts) / len(pcts)
            com_fogo = sum(1 for p in pcts if p > 0.0)
            print(f"  • Classe '{cls}':")
            print(f"      - Amostras processadas: {len(pcts)}")
            print(f"      - Amostras com pixels >= {threshold:.1f} °C: {com_fogo} ({com_fogo/len(pcts)*100:.1f}%)")
            print(f"      - Cobertura média de fogo por quadro: {media_pct:.3f}% dos pixels")

    print("=" * 80)
    return {"total_gerados": gerados_count, "metadados": metadados}


def main():
    parser = argparse.ArgumentParser(
        description="Gera máscaras binárias PNG a partir de arquivos TIFF térmicos do FLAME 3."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/data/CVSubset",
        help="Caminho raiz da pasta do dataset extraído (padrão: ml/data/CVSubset)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ml/data/masks",
        help="Diretório de destino para salvar as máscaras (padrão: ml/data/masks)."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Limiar térmico em °C para considerar fogo (padrão: 80.0 °C)."
    )
    parser.add_argument(
        "--binary-value",
        type=int,
        default=255,
        choices=[1, 255],
        help="Valor numérico do pixel de fogo na máscara PNG (padrão: 255 para visualização direta)."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Se informado, sobrescreve máscaras já existentes no destino."
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Desativa o salvamento automático do arquivo CSV de metadados das máscaras."
    )
    args = parser.parse_args()

    caminho_data = Path(args.data_dir).resolve()
    caminho_output = Path(args.output_dir).resolve()

    if not caminho_data.exists():
        print(f"❌ Diretório de dados não encontrado: {caminho_data}")
        sys.exit(1)

    processar_mascaras(
        data_dir=caminho_data,
        output_dir=caminho_output,
        threshold=args.threshold,
        binary_value=args.binary_value,
        overwrite=args.overwrite,
        save_metadata_csv=(not args.no_csv)
    )


if __name__ == "__main__":
    main()

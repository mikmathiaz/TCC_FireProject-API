#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Avaliação e Benchmark de Inferência (Test Split)
================================================================================
Objetivo:
    Avaliar o modelo U-Net treinado sobre o conjunto de teste contíguo (ml/data/split.csv)
    e computar métricas acadêmicas completas:
      - IoU (Intersection over Union / Jaccard Index)
      - F1-Score (Dice Coefficient)
      - Precisão (Precision)
      - Revocação (Recall / Sensibilidade)
      - Tempo de inferência por imagem em milissegundos (latência média, mediana e P95)

Relevância para a Defesa do TCC:
    1. O conjunto de teste contém quadros capturados no final do voo, nunca
       vistos pelo modelo durante o treino ou a validação de hiperparâmetros.
    2. A latência de inferência (ms/frame) comprova a viabilidade do sistema
       para monitoramento operacional e emissão de alertas em tempo real.
    3. Apresenta o comparativo entre a modalidade óptica (RGB) e térmica (Thermal),
       fornecendo os dados empíricos para a discussão de resultados.

Uso:
    python ml/scripts/evaluate.py --checkpoint ml/checkpoints/best_model_rgb.pth --modality rgb --data-dir ml/data/CVSubset
    python ml/scripts/evaluate.py --checkpoint ml/checkpoints/best_model_thermal.pth --modality thermal --data-dir ml/data/CVSubset
================================================================================
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Suporte a terminais Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Adiciona o diretório raiz do projeto ao sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader
    HAS_TORCH = True
    torch_no_grad = torch.no_grad
except ImportError:
    torch = None
    nn = Any
    DataLoader = Any
    HAS_TORCH = False
    torch_no_grad = lambda: (lambda fn: fn)

try:
    import segmentation_models_pytorch as smp
    HAS_SMP = True
except ImportError:
    smp = None
    HAS_SMP = False

import numpy as np
from ml.src.dataset import FlameSegmentationDataset, criar_dataloader


@torch_no_grad()
def avaliar_modelo(
    model: nn.Module,
    dataloader: DataLoader,
    device: torch.device,
    threshold: float = 0.5
) -> Dict[str, object]:
    """
    Executa a inferência sobre o DataLoader, calcula métricas de segmentação
    e afere rigorosamente o tempo de inferência (latência) por imagem em ms.
    """
    model.eval()
    is_cuda = (device.type == "cuda")

    # Warm-up do modelo e do pipeline CUDA
    iterador_warmup = iter(dataloader)
    for _ in range(min(5, len(dataloader))):
        try:
            lote_w = next(iterador_warmup)
            img_w = lote_w["image"].to(device)
            _ = model(img_w)
            if is_cuda:
                torch.cuda.synchronize()
        except StopIteration:
            break

    latencias_ms: List[float] = []

    # Acumuladores globais para cálculo de métricas
    tp_global = 0.0
    fp_global = 0.0
    fn_global = 0.0
    tn_global = 0.0

    # Acumuladores específicos por classe
    metricas_por_classe: Dict[str, Dict[str, float]] = {
        "Fire": {"tp": 0.0, "fp": 0.0, "fn": 0.0, "total_amostras": 0},
        "No Fire": {"tp": 0.0, "fp": 0.0, "fn": 0.0, "total_amostras": 0}
    }

    for lote in dataloader:
        images = lote["image"].to(device)
        masks = lote["mask"].to(device)
        classes = lote["classe"]

        # Medição precisa de latência por imagem
        if is_cuda:
            torch.cuda.synchronize()
        t0 = time.perf_counter()

        logits = model(images)

        if is_cuda:
            torch.cuda.synchronize()
        t1 = time.perf_counter()

        tempo_lote_ms = (t1 - t0) * 1000.0
        # Normaliza por tamanho do lote (batch size)
        tempo_por_img_ms = tempo_lote_ms / images.size(0)
        for _ in range(images.size(0)):
            latencias_ms.append(tempo_por_img_ms)

        probs = torch.sigmoid(logits)
        preds = (probs >= threshold).float()
        targets = (masks >= 0.5).float()

        # Acumula por lote
        for i in range(images.size(0)):
            p = preds[i]
            t = targets[i]
            cls_nome = classes[i]

            tp = (p * t).sum().item()
            fp = (p * (1.0 - t)).sum().item()
            fn = ((1.0 - p) * t).sum().item()
            tn = ((1.0 - p) * (1.0 - t)).sum().item()

            tp_global += tp
            fp_global += fp
            fn_global += fn
            tn_global += tn

            if cls_nome in metricas_por_classe:
                metricas_por_classe[cls_nome]["tp"] += tp
                metricas_por_classe[cls_nome]["fp"] += fp
                metricas_por_classe[cls_nome]["fn"] += fn
                metricas_por_classe[cls_nome]["total_amostras"] += 1

    eps = 1e-7

    # Métricas Globais
    iou_global = (tp_global + eps) / (tp_global + fp_global + fn_global + eps)
    prec_global = (tp_global + eps) / (tp_global + fp_global + eps)
    rec_global = (tp_global + eps) / (tp_global + fn_global + eps)
    f1_global = 2.0 * (prec_global * rec_global) / (prec_global + rec_global + eps)

    # Métricas Isoladas para a classe Fire
    fire_stats = metricas_por_classe["Fire"]
    tp_f = fire_stats["tp"]
    fp_f = fire_stats["fp"]
    fn_f = fire_stats["fn"]
    iou_fire = (tp_f + eps) / (tp_f + fp_f + fn_f + eps)
    prec_fire = (tp_f + eps) / (tp_f + fp_f + eps)
    rec_fire = (tp_f + eps) / (tp_f + fn_f + eps)
    f1_fire = 2.0 * (prec_fire * rec_fire) / (prec_fire + rec_fire + eps)

    # Métricas de Latência
    latencias_arr = np.array(latencias_ms)
    media_lat_ms = float(np.mean(latencias_arr))
    mediana_lat_ms = float(np.median(latencias_arr))
    desvio_lat_ms = float(np.std(latencias_arr))
    p95_lat_ms = float(np.percentile(latencias_arr, 95))
    fps_equivalente = 1000.0 / media_lat_ms if media_lat_ms > 0 else 0.0

    return {
        "metricas_globais": {
            "iou": float(iou_global),
            "f1": float(f1_global),
            "precisao": float(prec_global),
            "recall": float(rec_global)
        },
        "metricas_classe_fire": {
            "iou": float(iou_fire),
            "f1": float(f1_fire),
            "precisao": float(prec_fire),
            "recall": float(rec_fire),
            "amostras": int(fire_stats["total_amostras"])
        },
        "metricas_classe_nofire": {
            "falsos_positivos_pixels": int(metricas_por_classe["No Fire"]["fp"]),
            "amostras": int(metricas_por_classe["No Fire"]["total_amostras"])
        },
        "latencia_ms": {
            "media": round(media_lat_ms, 2),
            "mediana": round(mediana_lat_ms, 2),
            "desvio_padrao": round(desvio_lat_ms, 2),
            "p95": round(p95_lat_ms, 2),
            "fps_equivalente": round(fps_equivalente, 1)
        },
        "total_amostras_avaliadas": len(latencias_ms)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Avalia o modelo de segmentação U-Net no conjunto de teste e afere a latência."
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        required=True,
        help="Caminho do arquivo checkpoint (.pth) treinado."
    )
    parser.add_argument(
        "--modality",
        type=str,
        default=None,
        choices=["rgb", "thermal"],
        help="Modalidade ('rgb' ou 'thermal'). Se omitido, tenta inferir do checkpoint."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/data/CVSubset",
        help="Diretório onde estão as imagens (padrão: ml/data/CVSubset)."
    )
    parser.add_argument(
        "--mask-dir",
        type=str,
        default=None,
        help="Diretório das máscaras (padrão: ml/data/masks)."
    )
    parser.add_argument(
        "--split-csv",
        type=str,
        default="ml/data/split.csv",
        help="Caminho para o split.csv (padrão: ml/data/split.csv)."
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        choices=["train", "val", "test"],
        help="Conjunto do split a avaliar (padrão: 'test')."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Tamanho do lote para aferição de latência (padrão: 1 para latência por imagem)."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Limiar de binarização sigmóide (padrão: 0.5)."
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Caminho opcional para salvar o relatório de avaliação em formato JSON."
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Dispositivo de inferência ('cuda' ou 'cpu')."
    )
    args = parser.parse_args()

    if not HAS_TORCH or not HAS_SMP:
        print("❌ ERRO: PyTorch ou segmentation_models_pytorch não estão instalados.")
        sys.exit(1)

    caminho_ckpt = Path(args.checkpoint).resolve()
    if not caminho_ckpt.exists():
        print(f"❌ Checkpoint não encontrado: {caminho_ckpt}")
        sys.exit(1)

    device = torch.device(args.device if torch.cuda.is_available() and args.device == "cuda" else "cpu")

    # Carrega dados do checkpoint
    print(f"📂 Carregando checkpoint: {caminho_ckpt}")
    ckpt = torch.load(caminho_ckpt, map_location=device)

    modality = args.modality
    if modality is None:
        modality = ckpt.get("modality", "rgb")

    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=1
    ).to(device)

    model.load_state_dict(ckpt["model_state_dict"])

    # DataLoader
    dataloader = criar_dataloader(
        split_csv=args.split_csv,
        data_dir=args.data_dir,
        mask_dir=args.mask_dir,
        modality=modality,
        split=args.split,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0
    )

    print("=" * 80)
    print("🔬 FIRE WATCHER — RELATÓRIO DE AVALIAÇÃO DE DESEMPENHO")
    print("=" * 80)
    print(f"📦 Checkpoint:     {caminho_ckpt.name}")
    print(f"🎨 Modalidade:     {modality.upper()} ({'RGB Corrigido' if modality == 'rgb' else 'Thermal Raw JPG'})")
    print(f"📊 Conjunto:       {args.split.upper()} ({len(dataloader.dataset)} amostras)")
    print(f"💻 Dispositivo:    {device}")
    print("=" * 80)
    print("⏳ Processando inferência e computando métricas...")

    resultados = avaliar_modelo(
        model=model,
        dataloader=dataloader,
        device=device,
        threshold=args.threshold
    )

    glob = resultados["metricas_globais"]
    fire = resultados["metricas_classe_fire"]
    nofire = resultados["metricas_classe_nofire"]
    lat = resultados["latencia_ms"]

    print("\n" + "=" * 80)
    print("📈 1. MÉTRICAS ACADÊMICAS DE SEGMENTAÇÃO (TEST SPLIT)")
    print("=" * 80)
    print(f"  • IoU Global (Jaccard):       {glob['iou'] * 100:.2f}% ({glob['iou']:.4f})")
    print(f"  • F1-Score (Dice):            {glob['f1'] * 100:.2f}% ({glob['f1']:.4f})")
    print(f"  • Precisão:                   {glob['precisao'] * 100:.2f}% ({glob['precisao']:.4f})")
    print(f"  • Revocação (Recall):         {glob['recall'] * 100:.2f}% ({glob['recall']:.4f})")
    print("\n  Detalhe - Classe Fire (Focos Reais):")
    print(f"  • IoU na classe Fire:         {fire['iou'] * 100:.2f}% (em {fire['amostras']} quadros)")
    print(f"  • F1-Score na classe Fire:    {fire['f1'] * 100:.2f}%")
    print(f"  • Recall na classe Fire:      {fire['recall'] * 100:.2f}%")
    print("\n  Detalhe - Classe No Fire (Áreas sem Queimada):")
    print(f"  • Falsos Positivos:           {nofire['falsos_positivos_pixels']} pixels detectados indevidamente ({nofire['amostras']} quadros)")

    print("\n" + "=" * 80)
    print("⚡ 2. BENCHMARK DE LATÊNCIA E TEMPO DE INFERÊNCIA (TEMPO REAL)")
    print("=" * 80)
    print(f"  • Latência Média por Imagem:  {lat['media']:.2f} ms")
    print(f"  • Mediana:                    {lat['mediana']:.2f} ms (Desvio Padrão: ±{lat['desvio_padrao']:.2f} ms)")
    print(f"  • Percentil 95 (P95):         {lat['p95']:.2f} ms")
    print(f"  • Throughput Estimado:        {lat['fps_equivalente']:.1f} FPS (Quadros por Segundo)")
    print("=" * 80)

    if args.output_json:
        caminho_json = Path(args.output_json).resolve()
        caminho_json.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho_json, mode="w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Relatório JSON gravado em: {caminho_json}")


if __name__ == "__main__":
    main()

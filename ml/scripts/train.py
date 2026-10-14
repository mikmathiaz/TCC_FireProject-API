#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Treinamento do Modelo de Segmentação Semântica U-Net (FLAME 3)
================================================================================
Objetivo:
    Treinar a rede U-Net com encoder ResNet34 pré-treinado para segmentação
    binária de fogo (pixel a pixel) a partir de imagens aéreas de drone DJI M30T.
    Permite treinar nas modalidades:
      - 'rgb': RGB com campo de visão corrigido (640x512)
      - 'thermal': Imagem térmica em paleta de cor original (Raw JPG, 640x512)

Decisões de Projeto e Defesa Metodológica para o TCC:
    1. Arquitetura U-Net + ResNet34:
       - O encoder ResNet34 extrai padrões espaciais hierárquicos multiescala com
         pesos pré-treinados do ImageNet, enquanto os skip-connections do decodificador
         U-Net recuperam com precisão as bordas finas dos focos de chamas e brasas.
    2. Função de Perda Combinada (BCE + Dice):
       - A perda BCE (Binary Cross-Entropy) otimiza a classificação probabilística pixel a pixel.
       - A perda Dice foca na sobreposição espacial entre predição e máscara, sendo indispensável
         para combater o forte desbalanceamento de classes (fogo ocupa minoria dos pixels).
    3. Treinamento com Precisão Mista (AMP - Automatic Mixed Precision):
       - Acelera o processamento em GPUs modernas (NVIDIA T4 / V100 no Google Colab) e
         reduz o consumo de VRAM sem perda de precisão numérica.
    4. Checkpointing Retomável (--resume):
       - Salva o melhor modelo por IoU de validação ('best_model_{modality}.pth') e o último
         checkpoint a cada época ('last_checkpoint_{modality}.pth'), permitindo recuperar o
         treino em caso de desconexão da sessão do Colab.
    5. Modo Smoke Test (--smoke):
       - Treina em 8 imagens de fogo por 30 épocas para verificar capacidade de sobreajuste
         (overfitting intencional). Se IoU < 0.80, alerta imediatamente a presença de bug.

Uso:
    python ml/scripts/train.py --modality rgb --data-dir ml/data/CVSubset --epochs 40 --batch-size 4
    python ml/scripts/train.py --modality thermal --data-dir ml/data/CVSubset --epochs 40 --batch-size 4
    python ml/scripts/train.py --modality rgb --data-dir ml/data/CVSubset --smoke
================================================================================
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Any, Dict, Tuple

# Suporte a terminais Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Adiciona o diretório raiz do projeto ao sys.path para permitir importações de ml.src
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

from ml.src.dataset import FlameSegmentationDataset, criar_dataloader


def calcular_metricas_binarias(
    logits: torch.Tensor,
    targets: torch.Tensor,
    threshold: float = 0.5,
    eps: float = 1e-7
) -> Tuple[float, float, float, float]:
    """
    Calcula IoU (Jaccard), F1-Score (Dice), Precisão e Recall binários.
    """
    probs = torch.sigmoid(logits)
    preds = (probs >= threshold).float()
    targets = (targets >= 0.5).float()

    tp = (preds * targets).sum().item()
    fp = (preds * (1.0 - targets)).sum().item()
    fn = ((1.0 - preds) * targets).sum().item()

    iou = (tp + eps) / (tp + fp + fn + eps)
    precision = (tp + eps) / (tp + fp + eps)
    recall = (tp + eps) / (tp + fn + eps)
    f1 = 2.0 * (precision * recall) / (precision + recall + eps)

    return float(iou), float(f1), float(precision), float(recall)


def treinar_uma_epoca(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: torch.cuda.amp.GradScaler,
    device: torch.device,
    use_amp: bool
) -> float:
    """
    Executa uma época completa de treinamento e retorna a perda média.
    """
    model.train()
    loss_acumulada = 0.0
    total_lotes = 0

    for lote in dataloader:
        images = lote["image"].to(device, non_blocking=True)
        masks = lote["mask"].to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        with torch.cuda.amp.autocast(enabled=use_amp):
            logits = model(images)
            loss = criterion(logits, masks)

        if use_amp:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()

        loss_acumulada += loss.item()
        total_lotes += 1

    return loss_acumulada / max(1, total_lotes)


@torch_no_grad()
def validar(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    use_amp: bool
) -> Dict[str, float]:
    """
    Avalia o modelo no conjunto de validação e consolida perda e métricas.
    """
    model.eval()
    loss_acumulada = 0.0
    total_lotes = 0

    # Acumuladores globais para IoU, F1, Precisão e Recall
    tp_total = 0.0
    fp_total = 0.0
    fn_total = 0.0
    eps = 1e-7

    for lote in dataloader:
        images = lote["image"].to(device, non_blocking=True)
        masks = lote["mask"].to(device, non_blocking=True)

        with torch.cuda.amp.autocast(enabled=use_amp):
            logits = model(images)
            loss = criterion(logits, masks)

        loss_acumulada += loss.item()
        total_lotes += 1

        probs = torch.sigmoid(logits)
        preds = (probs >= 0.5).float()
        targets = (masks >= 0.5).float()

        tp_total += (preds * targets).sum().item()
        fp_total += (preds * (1.0 - targets)).sum().item()
        fn_total += ((1.0 - preds) * targets).sum().item()

    val_loss = loss_acumulada / max(1, total_lotes)
    val_iou = (tp_total + eps) / (tp_total + fp_total + fn_total + eps)
    val_precision = (tp_total + eps) / (tp_total + fp_total + eps)
    val_recall = (tp_total + eps) / (tp_total + fn_total + eps)
    val_f1 = 2.0 * (val_precision * val_recall) / (val_precision + val_recall + eps)

    return {
        "loss": float(val_loss),
        "iou": float(val_iou),
        "f1": float(val_f1),
        "precision": float(val_precision),
        "recall": float(val_recall)
    }


def executar_treinamento(args):
    if not HAS_TORCH or not HAS_SMP:
        print("❌ ERRO: PyTorch ou segmentation_models_pytorch não estão instalados.")
        print("Execute no Google Colab com: pip install -r ml/requirements-ml.txt")
        sys.exit(1)

    device = torch.device(args.device if torch.cuda.is_available() and args.device == "cuda" else "cpu")
    use_amp = (device.type == "cuda")

    data_dir = Path(args.data_dir).resolve()
    mask_dir = Path(args.mask_dir).resolve() if args.mask_dir else None
    split_csv = Path(args.split_csv).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    num_epocas = 30 if args.smoke else args.epochs

    print("=" * 80)
    print("🔥 FIRE WATCHER — PIPELINE DE TREINAMENTO U-NET (RESNET34)")
    print("=" * 80)
    print(f"📦 Modalidade de Entrada: {args.modality.upper()} "
          f"({'RGB/Corrected FOV' if args.modality == 'rgb' else 'Thermal/Raw JPG'})")
    print(f"💻 Dispositivo (Device):   {device} (AMP Acelerado: {use_amp})")
    print(f"📁 Diretório de Dados:     {data_dir}")
    print(f"📁 Arquivo de Split:       {split_csv}")
    print(f"💾 Diretório Checkpoints:  {output_dir}")
    print(f"🔄 Épocas:                 {num_epocas} | Batch Size: {args.batch_size} | LR: {args.lr}")
    print(f"🧪 Modo Smoke Test:        {args.smoke}")
    print("=" * 80)

    # 1. Carregamento dos DataLoaders
    if args.smoke:
        train_loader = criar_dataloader(
            split_csv=split_csv,
            data_dir=data_dir,
            mask_dir=mask_dir,
            modality=args.modality,
            split="train",
            batch_size=args.batch_size,
            is_smoke=True,
            num_workers=0
        )
        val_loader = train_loader  # Em smoke test, valida no mesmo conjunto para checar capacidade de overfit
    else:
        train_loader = criar_dataloader(
            split_csv=split_csv,
            data_dir=data_dir,
            mask_dir=mask_dir,
            modality=args.modality,
            split="train",
            batch_size=args.batch_size,
            num_workers=args.num_workers
        )
        val_loader = criar_dataloader(
            split_csv=split_csv,
            data_dir=data_dir,
            mask_dir=mask_dir,
            modality=args.modality,
            split="val",
            batch_size=args.batch_size,
            num_workers=args.num_workers
        )

    print(f"📊 Amostras carregadas: Treino = {len(train_loader.dataset)} | Validação = {len(val_loader.dataset)}")

    # 2. Definição da Arquitetura (U-Net com Encoder ResNet34)
    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights="imagenet",
        in_channels=3,
        classes=1
    ).to(device)

    # 3. Função de Perda Combinada: BCEWithLogits + Dice
    criterion_bce = nn.BCEWithLogitsLoss()
    criterion_dice = smp.losses.DiceLoss(mode="binary", from_logits=True)

    def criterion_combinada(logits, targets):
        return criterion_bce(logits, targets) + criterion_dice(logits, targets)

    # 4. Otimizador AdamW
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    start_epoch = 1
    best_val_iou = 0.0

    # Retomada de Checkpoint (--resume)
    if args.resume:
        caminho_resume = Path(args.resume).resolve()
        if caminho_resume.exists():
            print(f"\n🔄 Retomando treinamento a partir de: {caminho_resume}")
            ckpt = torch.load(caminho_resume, map_location=device)
            model.load_state_dict(ckpt["model_state_dict"])
            optimizer.load_state_dict(ckpt["optimizer_state_dict"])
            if "scaler_state_dict" in ckpt and use_amp:
                scaler.load_state_dict(ckpt["scaler_state_dict"])
            start_epoch = ckpt.get("epoch", 0) + 1
            best_val_iou = ckpt.get("best_val_iou", 0.0)
            print(f"   Iniciando na Época {start_epoch} (Melhor IoU anterior: {best_val_iou:.4f})")
        else:
            print(f"⚠️ Checkpoint de retomada não encontrado em '{caminho_resume}'. Iniciando do zero.")

    # Arquivo de Log CSV de Métricas por Época
    csv_log_path = output_dir / f"metrics_{args.modality}.csv"
    existe_csv = csv_log_path.exists() and (start_epoch > 1)

    f_log = open(csv_log_path, mode="a" if existe_csv else "w", newline="", encoding="utf-8")
    writer = csv.writer(f_log)
    if not existe_csv:
        writer.writerow(["epoch", "train_loss", "val_loss", "val_iou", "val_f1", "val_precision", "val_recall", "lr", "tempo_s"])
        f_log.flush()

    caminho_best = output_dir / f"best_model_{args.modality}.pth"
    caminho_last = output_dir / f"last_checkpoint_{args.modality}.pth"

    print("\n🚀 Iniciando ciclo de treinamento...\n")
    print("-" * 105)
    print(f"{'Época':^7} | {'Train Loss':^12} | {'Val Loss':^10} | {'Val IoU':^10} | {'Val F1':^10} | {'Precisão':^10} | {'Recall':^10} | {'Tempo':^7}")
    print("-" * 105)

    try:
        for epoca in range(start_epoch, num_epocas + 1):
            t_inicio = time.time()

            # Treino
            train_loss = treinar_uma_epoca(
                model=model,
                dataloader=train_loader,
                criterion=criterion_combinada,
                optimizer=optimizer,
                scaler=scaler,
                device=device,
                use_amp=use_amp
            )

            # Validação
            val_metrics = validar(
                model=model,
                dataloader=val_loader,
                criterion=criterion_combinada,
                device=device,
                use_amp=use_amp
            )

            t_decorrido = time.time() - t_inicio
            lr_atual = optimizer.param_groups[0]["lr"]

            # Registro no CSV
            writer.writerow([
                epoca,
                f"{train_loss:.4f}",
                f"{val_metrics['loss']:.4f}",
                f"{val_metrics['iou']:.4f}",
                f"{val_metrics['f1']:.4f}",
                f"{val_metrics['precision']:.4f}",
                f"{val_metrics['recall']:.4f}",
                f"{lr_atual:.2e}",
                f"{t_decorrido:.1f}"
            ])
            f_log.flush()

            # Checkpoint: Última Época
            checkpoint_data = {
                "epoch": epoca,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "scaler_state_dict": scaler.state_dict() if use_amp else None,
                "best_val_iou": best_val_iou,
                "val_metrics": val_metrics,
                "modality": args.modality,
                "args": vars(args)
            }
            torch.save(checkpoint_data, str(caminho_last))

            # Checkpoint: Melhor Modelo (Val IoU)
            eh_melhor = val_metrics["iou"] > best_val_iou
            destaque_melhor = ""
            if eh_melhor:
                best_val_iou = val_metrics["iou"]
                checkpoint_data["best_val_iou"] = best_val_iou
                torch.save(checkpoint_data, str(caminho_best))
                destaque_melhor = " ⭐ [NOVO MELHOR]"

            print(
                f"{epoca:03d}/{num_epocas:03d} | "
                f"{train_loss:^12.4f} | "
                f"{val_metrics['loss']:^10.4f} | "
                f"{val_metrics['iou']:^10.4f} | "
                f"{val_metrics['f1']:^10.4f} | "
                f"{val_metrics['precision']:^10.4f} | "
                f"{val_metrics['recall']:^10.4f} | "
                f"{t_decorrido:^6.1f}s{destaque_melhor}"
            )

    finally:
        f_log.close()

    print("-" * 105)
    print(f"\n🏁 Treinamento finalizado! Melhor Val IoU: {best_val_iou:.4f}")
    print(f"💾 Checkpoints gravados em: {output_dir}")
    print(f"📊 Relatório de métricas:   {csv_log_path}")

    # Validação do Modo Smoke Test
    if args.smoke:
        print("\n" + "=" * 80)
        print("🧪 VERIFICAÇÃO DO MODO SMOKE TEST:")
        print("=" * 80)
        if best_val_iou >= 0.80:
            print(f"✅ SUCESSO! Overfitting de sanidade atingido: IoU = {best_val_iou:.4f} >= 0.80.")
            print("   O pipeline, a loss e o modelo estão perfeitamente funcionais.")
        else:
            print(f"⚠️ ALERTA DE BUG: O modelo atingiu IoU = {best_val_iou:.4f} < 0.80 nas 8 amostras de fogo!")
            print("   Verifique a taxa de aprendizado, a normalização ou o alinhamento das máscaras.")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Treina o modelo de segmentação binária de fogo U-Net (FLAME 3)."
    )
    parser.add_argument(
        "--modality",
        type=str,
        required=True,
        choices=["rgb", "thermal"],
        help="Modalidade de entrada: 'rgb' (RGB/Corrected FOV) ou 'thermal' (Thermal/Raw JPG)."
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
        help="Diretório das máscaras (padrão: ml/data/masks ou dentro de data-dir)."
    )
    parser.add_argument(
        "--split-csv",
        type=str,
        default="ml/data/split.csv",
        help="Caminho para split.csv (padrão: ml/data/split.csv)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ml/checkpoints",
        help="Diretório para salvar modelos e métricas (padrão: ml/checkpoints)."
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=40,
        help="Número total de épocas (padrão: 40; em modo --smoke, fixa em 30)."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Tamanho do batch (padrão: 4)."
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=1e-4,
        help="Taxa de aprendizado inicial para AdamW (padrão: 1e-4)."
    )
    parser.add_argument(
        "--weight-decay",
        type=float,
        default=1e-4,
        help="Decaimento de peso para regularização (padrão: 1e-4)."
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Caminho do arquivo checkpoint (.pth) para continuar o treino."
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Modo Smoke Test: treina em 8 amostras por 30 épocas e checa se IoU >= 0.80."
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=2,
        help="Número de workers do DataLoader (padrão: 2)."
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Dispositivo de execução ('cuda' ou 'cpu')."
    )
    args = parser.parse_args()

    executar_treinamento(args)


if __name__ == "__main__":
    main()

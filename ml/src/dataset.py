#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Dataset PyTorch para Segmentação Semântica de Fogo (FLAME 3)
================================================================================
Objetivo:
    Mapear as amostras do dataset FLAME 3 a partir do arquivo 'split.csv',
    carregando a modalidade selecionada ('rgb' ou 'thermal') e a respectiva
    máscara de verdade de solo (640x512), aplicando aumentações exclusivamente
    geométricas para evitar distorções espectrais na paleta térmica.

Modalidades Suportadas:
    - 'rgb': Imagem óptica com campo de visão corrigido (RGB/Corrected FOV, 640x512, 3 canais)
    - 'thermal': Imagem térmica na paleta original da câmera (Thermal/Raw JPG, 640x512, 3 canais)
    - Máscara: PNG binário 640x512 (1 canal: 0.0 para fundo, 1.0 para fogo)

Decisões de Engenharia e Defesa para o TCC:
    1. Resolução Nativa: As imagens RGB corrigidas e Raw JPG já possuem exatamente
       a mesma resolução de 640x512 das máscaras, sem interpolações ou cortes artificiais.
    2. Aumentações Exclusivamente Geométricas (Albumentations):
       - No conjunto de treino: espelhamentos horizontal e vertical (HorizontalFlip, VerticalFlip),
         rotações ortogonais (RandomRotate90) e leves translações/rotações (ShiftScaleRotate).
       - Sem Color Jitter / Brightness no térmico: Alterar o brilho ou contraste da paleta
         térmica alteraria a pseudo-temperatura codificada visualmente nas cores da câmera,
         induzindo o modelo a erro.
    3. Normalização Padrão ImageNet:
       - O encoder ResNet34 pré-treinado no ImageNet espera tensores com média
         [0.485, 0.456, 0.406] e desvio-padrão [0.229, 0.224, 0.225].
================================================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from PIL import Image

try:
    import torch
    from torch.utils.data import DataLoader, Dataset
except ImportError:
    torch = None
    Dataset = object
    DataLoader = Any

try:
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    HAS_ALBUMENTATIONS = True
except ImportError:
    A = None
    ToTensorV2 = None
    HAS_ALBUMENTATIONS = False


def obter_transforms(split: str) -> Optional[object]:
    """
    Retorna a pipeline de transformações do Albumentations.
    Aumentações geométricas aplicadas apenas para 'train'.
    """
    if not HAS_ALBUMENTATIONS:
        return None

    if split == "train":
        return A.Compose([
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.05,
                scale_limit=0.08,
                rotate_limit=15,
                border_mode=0,
                p=0.5
            ),
            A.Normalize(
                mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)
            ),
            ToTensorV2()
        ])
    else:
        # Validação / Teste: apenas normalização estatística e conversão em tensor PyTorch
        return A.Compose([
            A.Normalize(
                mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)
            ),
            ToTensorV2()
        ])


class FlameSegmentationDataset(Dataset):
    """
    Dataset PyTorch para carregar amostras de fogo e não-fogo do FLAME 3.
    """
    def __init__(
        self,
        split_csv: Union[str, Path],
        data_dir: Union[str, Path],
        mask_dir: Optional[Union[str, Path]] = None,
        modality: str = "rgb",
        split: str = "train",
        transform: Optional[Callable] = None,
        is_smoke: bool = False
    ):
        """
        Args:
            split_csv: Caminho para o arquivo CSV de divisão (ex: ml/data/split.csv).
            data_dir: Diretório raiz onde estão as imagens (ou o bundle descompactado).
            mask_dir: Diretório das máscaras PNG (se None, assume data_dir / 'masks' ou data_dir).
            modality: 'rgb' (RGB/Corrected FOV) ou 'thermal' (Thermal/Raw JPG).
            split: 'train', 'val' ou 'test'.
            transform: Pipeline de transformações personalizada (se None, usa obter_transforms).
            is_smoke: Se True, seleciona 8 amostras com fogo para smoke-testing.
        """
        if torch is None:
            raise RuntimeError("PyTorch não está instalado no ambiente. O treino deve rodar com PyTorch.")

        self.modality = modality.lower().strip()
        if self.modality not in ["rgb", "thermal"]:
            raise ValueError(f"Modalidade inválida: '{modality}'. Escolha 'rgb' ou 'thermal'.")

        self.split = split.lower().strip()
        self.is_smoke = is_smoke
        self.data_dir = Path(data_dir).resolve()

        if mask_dir is not None:
            self.mask_dir = Path(mask_dir).resolve()
        else:
            # Tenta encontrar a pasta de máscaras dentro do próprio data_dir ou no padrão local
            if (self.data_dir / "masks").exists():
                self.mask_dir = self.data_dir / "masks"
            elif (self.data_dir / "Fire" / "Thermal" / "Celsius TIFF").exists():
                self.mask_dir = self.data_dir
            else:
                self.mask_dir = Path("ml/data/masks").resolve()

        self.split_csv_path = Path(split_csv).resolve()
        if not self.split_csv_path.exists():
            raise FileNotFoundError(f"Arquivo split.csv não encontrado em: {self.split_csv_path}")

        df_full = pd.read_csv(self.split_csv_path)

        if is_smoke:
            # Modo Smoke Test: seleciona exatamente 8 imagens com presença significativa de fogo
            df_fire = df_full[(df_full["classe"] == "Fire") & (df_full["pct_fogo"] > 1.0)]
            if len(df_fire) < 8:
                df_fire = df_full[df_full["classe"] == "Fire"]
            self.df = df_fire.head(8).reset_index(drop=True)
            print(f"🔥 [SMOKE MODE] Carregadas {len(self.df)} amostras de fogo para teste de overfitting.")
        else:
            self.df = df_full[df_full["split"] == self.split].reset_index(drop=True)

        if len(self.df) == 0:
            raise ValueError(f"Nenhum registro encontrado no split '{self.split}' em {self.split_csv_path}")

        # Em smoke mode (overfitting sanity check), desativa aumentações para testar memorização determinística
        split_transforms = "val" if self.is_smoke else self.split
        self.transform = transform if transform is not None else obter_transforms(split_transforms)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Dict[str, Union[torch.Tensor, str]]:
        row = self.df.iloc[idx]
        stem = str(row["amostra_id"])
        classe = str(row["classe"])

        # 1. Resolver caminho da imagem conforme a modalidade
        if self.modality == "rgb":
            rel_img = str(row["rgb_rel_path"])
        else:  # 'thermal'
            rel_img = str(row["thermal_raw_rel_path"])

        caminho_img = self.data_dir / rel_img
        if not caminho_img.exists():
            # Fallback tolerante para bundle com separador alternativo
            caminho_img_alt = self.data_dir / Path(rel_img)
            if caminho_img_alt.exists():
                caminho_img = caminho_img_alt
            else:
                raise FileNotFoundError(f"Imagem da modalidade '{self.modality}' não encontrada: {caminho_img}")

        # 2. Resolver caminho da máscara
        rel_mask = str(row["mask_rel_path"])
        caminho_mask = self.mask_dir / rel_mask
        if not caminho_mask.exists():
            caminho_mask_alt = self.mask_dir / Path(rel_mask)
            if caminho_mask_alt.exists():
                caminho_mask = caminho_mask_alt
            else:
                # Tenta buscar diretamente dentro de mask_dir / classe
                candidatos = list(self.mask_dir.rglob(f"{stem}.png"))
                if candidatos:
                    caminho_mask = candidatos[0]
                else:
                    raise FileNotFoundError(f"Máscara binária não encontrada: {caminho_mask}")

        # 3. Carregar imagem RGB (640x512, 3 canais)
        with Image.open(caminho_img) as pil_img:
            img_arr = np.array(pil_img.convert("RGB"), dtype=np.uint8)

        # 4. Carregar máscara (640x512, 1 canal binário: 0.0 ou 1.0)
        with Image.open(caminho_mask) as pil_mask:
            mask_arr = np.array(pil_mask.convert("L"), dtype=np.uint8)
            # Normaliza para 0.0 e 1.0 binário
            mask_bin = (mask_arr >= 128).astype(np.float32)

        # 5. Aplicação das transformações sincronizadas
        if self.transform is not None:
            augmented = self.transform(image=img_arr, mask=mask_bin)
            image_tensor = augmented["image"]  # (3, 512, 640)
            mask_tensor = augmented["mask"]    # (512, 640)
            if mask_tensor.ndim == 2:
                mask_tensor = mask_tensor.unsqueeze(0)  # (1, 512, 640)
        else:
            # Fallback sem Albumentations: converte manualmente para tensores
            image_tensor = torch.from_numpy(img_arr.transpose(2, 0, 1)).float() / 255.0
            # Normalização ImageNet
            mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
            image_tensor = (image_tensor - mean) / std
            mask_tensor = torch.from_numpy(mask_bin).float().unsqueeze(0)

        return {
            "image": image_tensor,
            "mask": mask_tensor,
            "amostra_id": stem,
            "classe": classe,
            "modality": self.modality
        }


def criar_dataloader(
    split_csv: Union[str, Path],
    data_dir: Union[str, Path],
    mask_dir: Optional[Union[str, Path]] = None,
    modality: str = "rgb",
    split: str = "train",
    batch_size: int = 4,
    shuffle: Optional[bool] = None,
    num_workers: int = 2,
    is_smoke: bool = False
) -> DataLoader:
    """
    Função facilitadora para instanciação do DataLoader PyTorch.
    """
    if torch is None:
        raise RuntimeError("PyTorch não instalado no ambiente local.")

    dataset = FlameSegmentationDataset(
        split_csv=split_csv,
        data_dir=data_dir,
        mask_dir=mask_dir,
        modality=modality,
        split=split,
        is_smoke=is_smoke
    )

    if shuffle is None:
        shuffle = (split == "train" and not is_smoke)

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=(split == "train" and len(dataset) > batch_size and not is_smoke)
    )

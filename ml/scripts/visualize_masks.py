#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Visualização e Conferência de Máscaras (Overlay RGB + Térmico)
================================================================================
Objetivo:
    Gerar composições visuais lado a lado (painéis comparativos) e sobreposições
    (overlay) da máscara binária de fogo projetada sobre a imagem óptica RGB corrigida
    e sobre o mapa térmico radiométrico do drone DJI M30T (FLAME 3).

Finalidade Acadêmica / Validação Metodológica para o TCC:
    1. O pesquisador e a banca podem inspecionar visualmente se o limiar físico
       adotado (ex: >= 80.0 °C) delimita com precisão os focos reais de fogo,
       brasas incandescentes (smoldering) e fumaça sem vazar para solo quente.
    2. Confirma se o canal RGB corrigido (640x512) está perfeitamente alinhado
       ao sensor térmico e à máscara gerada pixel a pixel.
    3. Rigor metodológico: assegura correspondência estrita de classe e arquivo
       entre RGB, TIFF e máscara, prevenindo contaminação cruzada.
    4. Amostragem representativa: seleciona quadros uniformemente espaçados na
       sequência temporal do voo, incluindo obrigatoriamente as amostras de
       maior e menor cobertura de fogo.

Painel Gerado para Cada Amostra:
    [1. RGB Corrigido] | [2. Térmico Radiométrico (°C)] | [3. Máscara Binária] | [4. Sobreposição (Overlay)]

Uso:
    python ml/scripts/visualize_masks.py --data-dir "C:/caminho/para/FLAME 3" --mask-dir ml/data/masks --output-dir ml/outputs/visualizations --num-samples 12
================================================================================
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Compatibilidade com terminais Windows (cp1252 / cmd / powershell)
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

# Suporte prioritário a tifffile com fallback para PIL
try:
    import tifffile
    HAS_TIFFFILE = True
except ImportError:
    tifffile = None
    HAS_TIFFFILE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    Image = None
    HAS_PIL = False

try:
    import matplotlib
    matplotlib.use("Agg")  # Backend não interativo para geração de arquivos
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    plt = None
    HAS_MATPLOTLIB = False


def carregar_tiff_temperatura(caminho_tiff: Path) -> np.ndarray:
    """
    Carrega matriz térmica float32 em °C a partir do arquivo TIFF radiométrico.
    """
    if HAS_TIFFFILE:
        matriz = tifffile.imread(str(caminho_tiff))
    elif HAS_PIL:
        img = Image.open(str(caminho_tiff))
        matriz = np.array(img)
    else:
        raise RuntimeError("Instale 'tifffile' ou 'Pillow' para carregar arquivos TIFF.")

    # Remove dimensões unitárias (ex: (1, 512, 640) -> (512, 640))
    if matriz.ndim == 3 and matriz.shape[0] == 1:
        matriz = matriz[0]
    elif matriz.ndim == 3 and matriz.shape[-1] == 1:
        matriz = matriz[:, :, 0]

    return matriz.astype(np.float32)


def carregar_mascara_binaria(caminho_mascara: Path) -> np.ndarray:
    """
    Carrega a máscara PNG binária como matriz uint8 2D (0 ou 255).
    """
    img = Image.open(str(caminho_mascara)).convert("L")
    return np.array(img, dtype=np.uint8)


def identificar_classe_de_caminho(caminho: Path) -> str:
    """
    Identifica de forma estrita se a amostra pertence a 'Fire' ou 'No Fire'.
    """
    partes = [p.lower().replace("_", " ").strip() for p in caminho.parts]
    if any("no fire" in p or "nofire" in p for p in partes):
        return "No Fire"
    elif any("fire" in p for p in partes):
        return "Fire"
    return "Desconhecido"


def resolver_trio_amostra(
    caminho_mascara: Path,
    mask_dir: Path,
    data_dir: Path
) -> Tuple[Path, Path, str, str]:
    """
    Localiza o arquivo TIFF e o arquivo RGB corrigido estritamente correspondentes
    à máscara informada, assegurando que pertençam à MESMA classe e ao MESMO stem (nome base).
    
    Retorna:
        Tuple[caminho_tiff, caminho_rgb_corrigido, classe, stem]
    """
    classe = identificar_classe_de_caminho(caminho_mascara)
    if classe == "Desconhecido":
        rel = caminho_mascara.relative_to(mask_dir)
        classe = "No Fire" if "no fire" in str(rel).lower() else "Fire"

    stem = caminho_mascara.stem  # Exemplo: "00001"

    # 1. Localização do TIFF térmico na MESMA classe
    # Ordem de tentativa:
    #   (a) Caminho canônico do FLAME 3: data_dir / classe / 'Thermal' / 'Celsius TIFF' / f'{stem}.TIFF'
    #   (b) Variações de extensão (.tif, .tiff, .TIF)
    #   (c) Busca restrita EXCLUSIVAMENTE ao subdiretório daquela classe
    candidatos_tiff = [
        data_dir / classe / "Thermal" / "Celsius TIFF" / f"{stem}.TIFF",
        data_dir / classe / "Thermal" / "Celsius TIFF" / f"{stem}.tif",
        data_dir / classe / "Thermal" / "Celsius TIFF" / f"{stem}.tiff",
        data_dir / classe / "Thermal" / "Celsius TIFF" / f"{stem}.TIF",
    ]
    tiff_path = next((c for c in candidatos_tiff if c.exists()), None)

    if not tiff_path:
        # Busca restrita estritamente à pasta da classe
        pasta_classe = data_dir / classe
        achados_tiff = [
            f for f in pasta_classe.rglob(f"{stem}.*")
            if f.suffix.lower() in [".tif", ".tiff"] and not f.name.startswith(".")
        ]
        if achados_tiff:
            tiff_path = achados_tiff[0]

    if not tiff_path or not tiff_path.exists():
        raise FileNotFoundError(
            f"Arquivo TIFF térmico para a amostra '{stem}' (Classe: {classe}) "
            f"não foi encontrado sob o diretório: {data_dir / classe}"
        )

    # 2. Localização do RGB Corrigido (640x512) na MESMA classe
    candidatos_rgb = [
        data_dir / classe / "RGB" / "Corrected FOV" / f"{stem}.JPG",
        data_dir / classe / "RGB" / "Corrected FOV" / f"{stem}.jpg",
        data_dir / classe / "RGB" / "Corrected FOV" / f"{stem}.jpeg",
        data_dir / classe / "RGB" / "Corrected FOV" / f"{stem}.png",
    ]
    rgb_path = next((c for c in candidatos_rgb if c.exists()), None)

    if not rgb_path:
        pasta_classe = data_dir / classe
        achados_rgb = [
            f for f in pasta_classe.rglob(f"{stem}.*")
            if f.suffix.lower() in [".jpg", ".jpeg", ".png"]
            and "thermal" not in f.name.lower()
            and ("corrected" in str(f).lower() or "fov" in str(f).lower())
            and not f.name.startswith(".")
        ]
        if achados_rgb:
            rgb_path = achados_rgb[0]

    if not rgb_path or not rgb_path.exists():
        raise FileNotFoundError(
            f"Arquivo RGB corrigido para a amostra '{stem}' (Classe: {classe}) "
            f"não foi encontrado sob o diretório: {data_dir / classe}"
        )

    # Validação de integridade: conferir se a pasta de origem pertence estritamente à classe esperada
    if classe not in tiff_path.parts:
        raise ValueError(f"Contaminação de classe: TIFF {tiff_path} não contém a classe '{classe}' em seu caminho.")
    if classe not in rgb_path.parts:
        raise ValueError(f"Contaminação de classe: RGB {rgb_path} não contém a classe '{classe}' em seu caminho.")

    return tiff_path, rgb_path, classe, stem


def aplicar_colormap_termico_pil(matriz_temp: np.ndarray) -> np.ndarray:
    """
    Gera representação RGB colorizada a partir da matriz térmica de °C
    usando interpolação de paleta quente (preto -> roxo -> laranja -> amarelo -> branco).
    Não depende do matplotlib, garantindo execução autônoma.
    """
    t_min = float(np.nanmin(matriz_temp))
    t_max = float(np.nanmax(matriz_temp))

    delta = max(1e-5, t_max - t_min)
    norm = np.clip((matriz_temp - t_min) / delta, 0.0, 1.0)

    h, w = matriz_temp.shape
    rgb_termico = np.zeros((h, w, 3), dtype=np.uint8)

    # 0.0 -> Preto [0, 0, 0]
    # 0.25 -> Roxo escuro [70, 0, 110]
    # 0.50 -> Vermelho vivo [210, 35, 10]
    # 0.75 -> Laranja/Amarelo [255, 175, 0]
    # 1.00 -> Branco incandescente [255, 255, 255]
    idx1 = norm < 0.25
    f1 = norm[idx1] / 0.25
    rgb_termico[idx1, 0] = (f1 * 70).astype(np.uint8)
    rgb_termico[idx1, 1] = 0
    rgb_termico[idx1, 2] = (f1 * 110).astype(np.uint8)

    idx2 = (norm >= 0.25) & (norm < 0.50)
    f2 = (norm[idx2] - 0.25) / 0.25
    rgb_termico[idx2, 0] = (70 + f2 * (210 - 70)).astype(np.uint8)
    rgb_termico[idx2, 1] = (f2 * 35).astype(np.uint8)
    rgb_termico[idx2, 2] = (110 - f2 * 100).astype(np.uint8)

    idx3 = (norm >= 0.50) & (norm < 0.75)
    f3 = (norm[idx3] - 0.50) / 0.25
    rgb_termico[idx3, 0] = (210 + f3 * 45).astype(np.uint8)
    rgb_termico[idx3, 1] = (35 + f3 * (175 - 35)).astype(np.uint8)
    rgb_termico[idx3, 2] = 10

    idx4 = norm >= 0.75
    f4 = (norm[idx4] - 0.75) / 0.25
    rgb_termico[idx4, 0] = 255
    rgb_termico[idx4, 1] = (175 + f4 * (255 - 175)).astype(np.uint8)
    rgb_termico[idx4, 2] = (10 + f4 * (255 - 10)).astype(np.uint8)

    return rgb_termico


def criar_sobreposicao(
    rgb_base: np.ndarray,
    mascara_binaria: np.ndarray,
    alpha: float = 0.45,
    cor_fogo: Tuple[int, int, int] = (255, 30, 20)
) -> np.ndarray:
    """
    Projeta a máscara de fogo sobre a imagem RGB com transparência ajustada.
    """
    overlay = rgb_base.copy().astype(np.float32)
    fogo_pixels = (mascara_binaria > 0)

    if np.any(fogo_pixels):
        cor_matriz = np.array(cor_fogo, dtype=np.float32)
        overlay[fogo_pixels] = (1.0 - alpha) * overlay[fogo_pixels] + alpha * cor_matriz

    return np.clip(overlay, 0, 255).astype(np.uint8)


def renderizar_painel_matplotlib(
    caminho_saida: Path,
    classe: str,
    nome_amostra: str,
    nome_rgb: str,
    nome_tiff: str,
    nome_mascara: str,
    rgb_img: np.ndarray,
    matriz_temp: np.ndarray,
    mascara: np.ndarray,
    overlay: np.ndarray,
    temp_min: float,
    temp_max: float,
    pct_fogo: float,
    limiar: float,
    tag_especial: str = ""
) -> None:
    """
    Renderiza composição com 4 subplots de alta qualidade usando Matplotlib.
    Inclui os nomes dos três arquivos no cabeçalho geral e nos subplots.
    """
    fig, axes = plt.subplots(1, 4, figsize=(21, 5.8), dpi=150)

    # Título geral de destaque contendo os 3 arquivos
    titulo_geral = (
        f"[{classe.upper()}{tag_especial}] Amostra: {nome_amostra}   |   "
        f"RGB: {nome_rgb}   •   TIFF: {nome_tiff}   •   Máscara: {nome_mascara}\n"
        f"T_max lido do TIFF: {temp_max:.1f} °C (T_min: {temp_min:.1f} °C, Limiar >= {limiar:.1f} °C)   |   "
        f"Área Queimada: {pct_fogo:.2f}% dos pixels ({int(np.sum(mascara > 0)):,} px)"
    )
    fig.suptitle(titulo_geral, fontsize=11, fontweight="bold", y=0.98)

    # 1. RGB
    axes[0].imshow(rgb_img)
    axes[0].set_title(f"1. RGB Corrigido\n({nome_rgb})", fontsize=10, fontweight="semibold")
    axes[0].axis("off")

    # 2. Térmico
    im_term = axes[1].imshow(matriz_temp, cmap="inferno")
    axes[1].set_title(f"2. Térmico Radiométrico\n({nome_tiff}) [{temp_min:.1f} a {temp_max:.1f} °C]", fontsize=10, fontweight="semibold")
    axes[1].axis("off")
    cbar = plt.colorbar(im_term, ax=axes[1], orientation="horizontal", pad=0.04, shrink=0.85)
    cbar.ax.tick_params(labelsize=8)

    # 3. Máscara
    axes[2].imshow(mascara, cmap="gray", vmin=0, vmax=255)
    axes[2].set_title(f"3. Máscara Binária\n({nome_mascara}) [{pct_fogo:.2f}% Fogo]", fontsize=10, fontweight="semibold")
    axes[2].axis("off")

    # 4. Overlay
    axes[3].imshow(overlay)
    axes[3].set_title("4. Sobreposição\n(RGB Corrigido + Máscara Fogo)", fontsize=10, fontweight="semibold")
    axes[3].axis("off")

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(caminho_saida), bbox_inches="tight")
    plt.close(fig)


def renderizar_painel_pil(
    caminho_saida: Path,
    classe: str,
    nome_amostra: str,
    nome_rgb: str,
    nome_tiff: str,
    nome_mascara: str,
    rgb_img: np.ndarray,
    matriz_temp: np.ndarray,
    mascara: np.ndarray,
    overlay: np.ndarray,
    temp_min: float,
    temp_max: float,
    pct_fogo: float,
    limiar: float,
    tag_especial: str = ""
) -> None:
    """
    Fallback autônomo usando pure PIL e NumPy para salvar o painel sem Matplotlib.
    """
    h, w, _ = rgb_img.shape

    img_rgb = Image.fromarray(rgb_img)
    term_color = aplicar_colormap_termico_pil(matriz_temp)
    img_term = Image.fromarray(term_color)
    mask_3c = np.stack([mascara] * 3, axis=-1)
    img_mask = Image.fromarray(mask_3c)
    img_overlay = Image.fromarray(overlay)

    altura_header = 55
    largura_total = w * 4 + 30
    altura_total = h + altura_header + 10

    painel = Image.new("RGB", (largura_total, altura_total), (18, 22, 32))
    draw = ImageDraw.Draw(painel)

    linha1 = f"[{classe.upper()}{tag_especial}] Amostra: {nome_amostra} | RGB: {nome_rgb} | TIFF: {nome_tiff} | Máscara: {nome_mascara}"
    linha2 = f"T_max TIFF: {temp_max:.1f}°C (Limiar: >={limiar:.1f}°C) | Fogo: {pct_fogo:.2f}% pixels"
    draw.text((15, 8), linha1, fill=(255, 255, 255))
    draw.text((15, 28), linha2, fill=(200, 220, 255))

    x_offset = 5
    y_offset = altura_header
    for img_bloco, legenda in [
        (img_rgb, f"1. RGB Corrigido ({nome_rgb})"),
        (img_term, f"2. Térmico ({nome_tiff}) [{temp_min:.0f}C a {temp_max:.0f}C]"),
        (img_mask, f"3. Máscara ({nome_mascara}) [{pct_fogo:.2f}%]"),
        (img_overlay, "4. Sobreposição RGB+Fogo")
    ]:
        painel.paste(img_bloco, (x_offset, y_offset))
        draw.text((x_offset + 5, y_offset + 5), legenda, fill=(255, 255, 255))
        x_offset += w + 8

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    painel.save(str(caminho_saida), format="PNG")


def carregar_tabela_cobertura(mask_dir: Path) -> Dict[Tuple[str, str], float]:
    """
    Carrega o mapeamento (classe_lower, stem_lower) -> pct_fogo a partir de masks_metadata.csv.
    """
    mapa: Dict[Tuple[str, str], float] = {}
    csv_path = mask_dir / "masks_metadata.csv"
    if csv_path.exists():
        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cls_key = row.get("classe", "").strip().lower()
                    m_arq = row.get("arquivo_mascara", "")
                    stem_key = Path(m_arq).stem.lower()
                    pct_val = float(row.get("pct_fogo", 0.0))
                    mapa[(cls_key, stem_key)] = pct_val
        except Exception:
            pass
    return mapa


def selecionar_amostras_com_extremos(
    amostras_paths: List[Path],
    num_samples: int,
    classe: str,
    cobertura_mapa: Dict[Tuple[str, str], float]
) -> List[Tuple[Path, str]]:
    """
    Seleciona amostras uniformemente espaçadas ao longo da sequência temporal,
    garantindo a inclusão obrigatória da amostra com MAIOR cobertura de fogo
    e da amostra com MENOR cobertura de fogo.
    
    Retorna lista de tuplas: (caminho_mascara, tag_especial)
    """
    total = len(amostras_paths)
    if total == 0:
        return []
    if total <= num_samples:
        return [(p, "") for p in amostras_paths]

    # Obter pct_fogo para cada amostra da sequência ordenada
    cls_key = classe.strip().lower()
    pcts: List[float] = []
    for p in amostras_paths:
        stem_key = p.stem.lower()
        if (cls_key, stem_key) in cobertura_mapa:
            pcts.append(cobertura_mapa[(cls_key, stem_key)])
        else:
            try:
                arr = np.array(Image.open(p))
                pct = (float(np.count_nonzero(arr > 0)) / float(arr.size)) * 100.0
                pcts.append(pct)
            except Exception:
                pcts.append(0.0)

    pcts_arr = np.array(pcts, dtype=np.float32)
    idx_max = int(np.argmax(pcts_arr))
    idx_min = int(np.argmin(pcts_arr))

    # Base com espaçamento uniforme na linha do tempo
    indices_base = list(np.linspace(0, total - 1, num_samples, dtype=int))

    def inserir_indice_especial(indices: List[int], alvo: int, protegidos: set) -> List[int]:
        if alvo in indices:
            return indices
        # Candidatos elegíveis: elementos do interior que não sejam protegidos
        candidatos = [idx for idx in indices[1:-1] if idx not in protegidos]
        if not candidatos:
            indices.append(alvo)
            return indices
        mais_proximo = min(candidatos, key=lambda idx: abs(idx - alvo))
        pos = indices.index(mais_proximo)
        indices[pos] = alvo
        return indices

    indices_selecionados = list(indices_base)
    # Protege os extremos temporais (0 e total-1) e os índices especiais entre si
    indices_selecionados = inserir_indice_especial(indices_selecionados, idx_max, {idx_min, 0, total - 1})
    indices_selecionados = inserir_indice_especial(indices_selecionados, idx_min, {idx_max, 0, total - 1})
    indices_selecionados = sorted(list(dict.fromkeys(indices_selecionados)))

    resultado: List[Tuple[Path, str]] = []
    for idx in indices_selecionados:
        tag = ""
        if idx == idx_max and pcts_arr[idx] > 0.0:
            tag = " [MÁXIMO FOGO]"
        elif idx == idx_min and classe.lower() == "fire":
            tag = " [MÍNIMO FOGO]"
        resultado.append((amostras_paths[idx], tag))

    return resultado


def executar_visualizacoes(
    data_dir: Path,
    mask_dir: Path,
    output_dir: Path,
    num_samples: int = 12,
    alpha: float = 0.45,
    threshold: float = 80.0
) -> None:
    """
    Percorre as máscaras geradas e produz as composições visuais lado a lado.
    """
    mascaras = sorted(list(mask_dir.rglob("*.png")))
    if not mascaras:
        print(f"❌ Nenhuma máscara encontrada em '{mask_dir}'.")
        print("Execute primeiro: python ml/scripts/generate_masks.py")
        return

    # Separação estrita por classe
    mascaras_por_classe: Dict[str, List[Path]] = {"Fire": [], "No Fire": []}
    for m in mascaras:
        cls = identificar_classe_de_caminho(m)
        if cls in mascaras_por_classe:
            mascaras_por_classe[cls].append(m)

    print("\n" + "=" * 80)
    print("🔥 FIRE WATCHER — GERAÇÃO DE PAINÉIS DE CONFERÊNCIA VISUAL")
    print("=" * 80)
    print(f"📁 Dataset FLAME 3:          {data_dir}")
    print(f"📁 Máscaras Binárias:         {mask_dir}")
    print(f"📁 Destino das Visualizações: {output_dir}")
    print(f"🌡️  Limiar Físico de Fogo:    >= {threshold:.1f} °C")
    print(f"🔍 Máscaras Encontradas:      {len(mascaras)} total "
          f"({len(mascaras_por_classe['Fire'])} Fire, {len(mascaras_por_classe['No Fire'])} No Fire)")
    print(f"🖼️  Backend de Renderização:   {'Matplotlib (figura acadêmica)' if HAS_MATPLOTLIB else 'Pillow/NumPy (nativo)'}")
    print("=" * 80)

    # Carrega mapa de cobertura para seleção otimizada
    cobertura_mapa = carregar_tabela_cobertura(mask_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    total_geradas = 0

    for cls in ["Fire", "No Fire"]:
        amostras_cls = mascaras_por_classe[cls]
        if not amostras_cls:
            continue

        amostras_selecionadas = selecionar_amostras_com_extremos(
            amostras_paths=amostras_cls,
            num_samples=num_samples,
            classe=cls,
            cobertura_mapa=cobertura_mapa
        )

        print(f"\n--- Gerando painéis para a classe '{cls}' ({len(amostras_selecionadas)} amostras selecionadas) ---")
        
        for idx_seq, (m_path, tag_especial) in enumerate(amostras_selecionadas, 1):
            # 1. Resolve o trio rigorosamente validado (mesma classe e mesmo arquivo)
            try:
                tiff_path, rgb_path, classe_resolvida, stem = resolver_trio_amostra(
                    caminho_mascara=m_path,
                    mask_dir=mask_dir,
                    data_dir=data_dir
                )
            except Exception as e:
                print(f"  ❌ Falha ao resolver arquivos para '{m_path.name}': {e}")
                continue

            # 2. Carrega matrizes
            try:
                matriz_temp = carregar_tiff_temperatura(tiff_path)
                mascara_bin = carregar_mascara_binaria(m_path)
            except Exception as e:
                print(f"  ❌ Erro ao ler TIFF/Máscara para '{stem}': {e}")
                continue

            # 3. Estatísticas térmicas extraídas do TIFF atualmente sendo exibido
            t_min = float(np.nanmin(matriz_temp))
            t_max = float(np.nanmax(matriz_temp))
            total_px = mascara_bin.size
            fogo_px = int(np.sum(mascara_bin > 0))
            pct_fogo = (fogo_px / total_px) * 100.0

            # 4. VERIFICAÇÃO CRÍTICA DE CONSISTÊNCIA SOLICITADA:
            # Se a máscara tem pixels de fogo e o T_max do TIFF exibido é menor que o limiar, para com erro!
            if fogo_px > 0 and t_max < threshold:
                raise RuntimeError(
                    f"\n❌ ERRO DE CONSISTÊNCIA CRÍTICA detectado na amostra '{stem}' (Classe: {classe_resolvida}):\n"
                    f"  • A máscara binária possui {fogo_px} pixels marcados como fogo (>= {threshold:.1f} °C).\n"
                    f"  • Porém, o TIFF exibido ({tiff_path.name}) possui T_max = {t_max:.2f} °C, menor que o limiar ({threshold:.1f} °C)!\n"
                    f"  • Arquivo TIFF usado:    {tiff_path}\n"
                    f"  • Arquivo Máscara usada: {m_path}\n"
                    f"  • Arquivo RGB usado:     {rgb_path}\n"
                    f"Isso indica contaminação ou incompatibilidade entre os arquivos. Execução interrompida imediatamente."
                )

            # 5. Carrega o RGB Corrigido
            try:
                with Image.open(str(rgb_path)) as im_rgb:
                    img_rgb = np.array(im_rgb.convert("RGB"))
                if img_rgb.shape[:2] != matriz_temp.shape[:2]:
                    img_pil = Image.fromarray(img_rgb).resize((matriz_temp.shape[1], matriz_temp.shape[0]))
                    img_rgb = np.array(img_pil)
            except Exception as e:
                print(f"  ⚠️ Não foi possível carregar RGB ({rgb_path.name}): {e}. Usando mapa térmico como base.")
                img_rgb = aplicar_colormap_termico_pil(matriz_temp)

            # 6. Gera sobreposição
            overlay = criar_sobreposicao(img_rgb, mascara_bin, alpha=alpha)

            # 7. Salva o painel visual
            nome_saida = f"overlay_{cls.lower().replace(' ', '_')}_{stem}.png"
            caminho_final = output_dir / nome_saida

            if HAS_MATPLOTLIB:
                renderizar_painel_matplotlib(
                    caminho_saida=caminho_final,
                    classe=cls,
                    nome_amostra=stem,
                    nome_rgb=rgb_path.name,
                    nome_tiff=tiff_path.name,
                    nome_mascara=m_path.name,
                    rgb_img=img_rgb,
                    matriz_temp=matriz_temp,
                    mascara=mascara_bin,
                    overlay=overlay,
                    temp_min=t_min,
                    temp_max=t_max,
                    pct_fogo=pct_fogo,
                    limiar=threshold,
                    tag_especial=tag_especial
                )
            else:
                renderizar_painel_pil(
                    caminho_saida=caminho_final,
                    classe=cls,
                    nome_amostra=stem,
                    nome_rgb=rgb_path.name,
                    nome_tiff=tiff_path.name,
                    nome_mascara=m_path.name,
                    rgb_img=img_rgb,
                    matriz_temp=matriz_temp,
                    mascara=mascara_bin,
                    overlay=overlay,
                    temp_min=t_min,
                    temp_max=t_max,
                    pct_fogo=pct_fogo,
                    limiar=threshold,
                    tag_especial=tag_especial
                )

            tag_log = f"{tag_especial} " if tag_especial else ""
            print(
                f"  [{idx_seq:02d}/{len(amostras_selecionadas):02d}] ✅ Painel gerado: {nome_saida} "
                f"[RGB: {rgb_path.name} | TIFF: {tiff_path.name} | Máscara: {m_path.name}] "
                f"(T_max: {t_max:.1f} °C, Fogo: {pct_fogo:.2f}%{tag_log})"
            )
            total_geradas += 1

    print("\n" + "=" * 80)
    print(f"🏁 Finalizado com sucesso! {total_geradas} painéis visuais salvos em:")
    print(f"   {output_dir}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Gera composições visuais de sobreposição (RGB + Térmico + Máscara) para conferência."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="ml/data/CVSubset",
        help="Caminho raiz da pasta do dataset extraído (padrão: ml/data/CVSubset)."
    )
    parser.add_argument(
        "--mask-dir",
        type=str,
        default="ml/data/masks",
        help="Diretório onde estão as máscaras PNG geradas (padrão: ml/data/masks)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ml/outputs/visualizations",
        help="Diretório onde salvar os painéis de visualização (padrão: ml/outputs/visualizations)."
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=12,
        help="Quantidade de amostras a visualizar por classe (padrão: 12)."
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.45,
        help="Transparência da sobreposição de fogo sobre o RGB (padrão: 0.45)."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Limiar térmico de referência em °C (padrão: 80.0 °C)."
    )
    args = parser.parse_args()

    executar_visualizacoes(
        data_dir=Path(args.data_dir).resolve(),
        mask_dir=Path(args.mask_dir).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        num_samples=args.num_samples,
        alpha=args.alpha,
        threshold=args.threshold
    )


if __name__ == "__main__":
    main()

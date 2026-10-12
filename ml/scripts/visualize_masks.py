#!/usr/bin/env python3
"""
================================================================================
Fire Watcher — Visualização e Conferência de Máscaras (Overlay RGB + Térmico)
================================================================================
Objetivo:
    Gerar composições visuais lado a lado (painéis comparativos) e sobreposições
    (overlay) da máscara binária de fogo projetada sobre a imagem óptica RGB corrigida
    e sobre o mapa térmico radiométrico do drone DJI M30T (FLAME 3).

Finalidade Acadêmica / Validação Visual:
    - O pesquisador e a banca de TCC podem inspecionar visualmente se o limiar
      físico adotado (ex: >= 80.0 °C) delimita com precisão os focos reais de fogo,
      brasas e fumaça sem vazar para solo quente ou copas não queimadas.
    - Confirma se o canal RGB corrigido (640x512) está perfeitamente alinhado
      ao sensor térmico e à máscara gerada.

Painel Gerado para Cada Amostra:
    [1. RGB Corrigido] | [2. Térmico Radiométrico (°C)] | [3. Máscara Binária] | [4. Sobreposição (Overlay)]

Uso:
    python ml/scripts/visualize_masks.py --data-dir ml/data/CVSubset --mask-dir ml/data/masks --output-dir ml/outputs/visualizations --num-samples 5
================================================================================
"""

import argparse
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
    Carrega matriz térmica float32 em °C.
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


def carregar_mascara_binaria(caminho_mascara: Path) -> np.ndarray:
    """
    Carrega a máscara PNG binária como matriz uint8 2D (0 ou 255).
    """
    img = Image.open(str(caminho_mascara)).convert("L")
    return np.array(img, dtype=np.uint8)


def encontrar_rgb_corrigido(caminho_tiff: Path, data_dir: Path) -> Optional[Path]:
    """
    Localiza o arquivo RGB corrigido (640x512) correspondente ao TIFF térmico.
    
    Estratégia de Busca:
        1. Procura na mesma pasta ou subpastas afins por arquivos .jpg com o mesmo stem.
        2. Procura arquivos contendo termos como 'rgb', 'corrected', ou 'fov'.
        3. Valida a resolução: o RGB bruto é 4000x3000; o corrigido é 640x512.
    """
    stem_base = caminho_tiff.stem.replace("_thermal", "").replace("_therm", "").replace("_TIFF", "").replace("_tiff", "")
    pasta_amostra = caminho_tiff.parent

    # Candidatos potenciais na vizinhança
    candidatos_locais = list(pasta_amostra.glob(f"*{stem_base}*.jpg")) + list(pasta_amostra.glob(f"*{stem_base}*.JPG"))
    
    # Se a estrutura for separada em subpastas irmãs (ex: Thermal_TIFF/ vs RGB_Corrected/)
    pasta_pai = pasta_amostra.parent
    candidatos_pai = list(pasta_pai.rglob(f"*{stem_base}*.jpg")) + list(pasta_pai.rglob(f"*{stem_base}*.JPG"))

    todos_candidatos = list(dict.fromkeys(candidatos_locais + candidatos_pai))

    candidato_ideal: Optional[Path] = None

    for cand in todos_candidatos:
        cand_str = cand.name.lower()
        # Se contiver 'corrected' ou 'cor' e for jpg
        if ("corrected" in cand_str or "fov" in cand_str) and cand.suffix.lower() in [".jpg", ".jpeg"]:
            return cand

    # Se não houver nome explícito, verifica pela resolução (640x512)
    for cand in todos_candidatos:
        if cand.suffix.lower() in [".jpg", ".jpeg"] and "thermal" not in cand.name.lower():
            try:
                with Image.open(str(cand)) as im:
                    w, h = im.size
                    if (w, h) in [(640, 512), (512, 640)]:
                        return cand
            except Exception:
                continue

    # Fallback: primeiro JPG não térmico encontrado associado ao stem
    for cand in todos_candidatos:
        if "thermal" not in cand.name.lower():
            return cand

    return None


def aplicar_colormap_termico_pil(matriz_temp: np.ndarray) -> np.ndarray:
    """
    Gera representação RGB colorizada a partir da matriz térmica de °C
    usando interpolação de paleta quente (preto -> roxo -> laranja -> amarelo -> branco).
    Não depende do matplotlib, garantindo execução autônoma.
    """
    t_min = float(np.nanmin(matriz_temp))
    t_max = float(np.nanmax(matriz_temp))
    
    # Normalização entre 0.0 e 1.0 (evitando divisão por zero)
    delta = max(1e-5, t_max - t_min)
    norm = np.clip((matriz_temp - t_min) / delta, 0.0, 1.0)

    h, w = matriz_temp.shape
    rgb_termico = np.zeros((h, w, 3), dtype=np.uint8)

    # Cores de controle para a rampa de calor:
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
    Destaca a área de fogo com uma mesclagem suave e borda visível.
    """
    overlay = rgb_base.copy().astype(np.float32)
    fogo_pixels = (mascara_binaria > 0)

    if np.any(fogo_pixels):
        cor_matriz = np.array(cor_fogo, dtype=np.float32)
        # Mesclagem alpha: (1 - alpha) * original + alpha * cor_destaque
        overlay[fogo_pixels] = (1.0 - alpha) * overlay[fogo_pixels] + alpha * cor_matriz

    return np.clip(overlay, 0, 255).astype(np.uint8)


def renderizar_painel_matplotlib(
    caminho_saida: Path,
    nome_amostra: str,
    rgb_img: np.ndarray,
    matriz_temp: np.ndarray,
    mascara: np.ndarray,
    overlay: np.ndarray,
    temp_min: float,
    temp_max: float,
    pct_fogo: float,
    limiar: float
) -> None:
    """
    Renderiza composição com 4 subplots de alta qualidade usando Matplotlib.
    """
    fig, axes = plt.subplots(1, 4, figsize=(20, 5), dpi=150)
    fig.suptitle(
        f"Amostra: {nome_amostra} | Limiar Fogo: >= {limiar:.1f} °C | "
        f"Área Queimada: {pct_fogo:.2f}% dos pixels | T_max: {temp_max:.1f} °C",
        fontsize=14,
        fontweight="bold",
        y=0.98
    )

    # 1. RGB
    axes[0].imshow(rgb_img)
    axes[0].set_title("1. RGB Corrigido (DJI M30T)", fontsize=11, fontweight="semibold")
    axes[0].axis("off")

    # 2. Térmico
    im_term = axes[1].imshow(matriz_temp, cmap="inferno")
    axes[1].set_title(f"2. Térmico Radiométrico ({temp_min:.1f} a {temp_max:.1f} °C)", fontsize=11, fontweight="semibold")
    axes[1].axis("off")
    cbar = plt.colorbar(im_term, ax=axes[1], orientation="horizontal", pad=0.03, shrink=0.85)
    cbar.ax.tick_params(labelsize=8)

    # 3. Máscara
    axes[2].imshow(mascara, cmap="gray", vmin=0, vmax=255)
    axes[2].set_title(f"3. Máscara Binária ({pct_fogo:.2f}% Fogo)", fontsize=11, fontweight="semibold")
    axes[2].axis("off")

    # 4. Overlay
    axes[3].imshow(overlay)
    axes[3].set_title("4. Sobreposição (RGB + Fogo)", fontsize=11, fontweight="semibold")
    axes[3].axis("off")

    plt.tight_layout()
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(caminho_saida), bbox_inches="tight")
    plt.close(fig)


def renderizar_painel_pil(
    caminho_saida: Path,
    nome_amostra: str,
    rgb_img: np.ndarray,
    matriz_temp: np.ndarray,
    mascara: np.ndarray,
    overlay: np.ndarray,
    temp_min: float,
    temp_max: float,
    pct_fogo: float,
    limiar: float
) -> None:
    """
    Fallback autônomo usando pure PIL e NumPy para concatenar horizontalmente
    os 4 quadros e salvar a composição sem exigir Matplotlib.
    """
    h, w, _ = rgb_img.shape

    # 1. Imagem RGB
    img_rgb = Image.fromarray(rgb_img)

    # 2. Imagem Térmica colorizada
    term_color = aplicar_colormap_termico_pil(matriz_temp)
    img_term = Image.fromarray(term_color)

    # 3. Máscara 3 canais para alinhamento
    mask_3c = np.stack([mascara] * 3, axis=-1)
    img_mask = Image.fromarray(mask_3c)

    # 4. Overlay
    img_overlay = Image.fromarray(overlay)

    # Cria painel combinado: altura h + cabeçalho, largura 4 * w
    altura_header = 40
    largura_total = w * 4 + 30
    altura_total = h + altura_header + 10

    painel = Image.new("RGB", (largura_total, altura_total), (18, 22, 32))
    draw = ImageDraw.Draw(painel)

    # Título geral
    titulo = f"Amostra: {nome_amostra} | Limiar: >={limiar:.1f}°C | Fogo: {pct_fogo:.2f}% pixels | T_max: {temp_max:.1f}°C"
    draw.text((15, 12), titulo, fill=(255, 255, 255))

    # Colagem dos 4 painéis
    x_offset = 5
    y_offset = altura_header
    for img_bloco, legenda in [
        (img_rgb, "1. RGB Corrigido"),
        (img_term, f"2. Térmico ({temp_min:.0f}C a {temp_max:.0f}C)"),
        (img_mask, "3. Máscara Binária"),
        (img_overlay, "4. Sobreposição RGB+Fogo")
    ]:
        painel.paste(img_bloco, (x_offset, y_offset))
        draw.text((x_offset + 5, y_offset + 5), legenda, fill=(255, 255, 255))
        x_offset += w + 8

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    painel.save(str(caminho_saida), format="PNG")


def executar_visualizacoes(
    data_dir: Path,
    mask_dir: Path,
    output_dir: Path,
    num_samples: int = 5,
    alpha: float = 0.45,
    threshold: float = 80.0
) -> None:
    """
    Percorre as máscaras geradas e produz as composições comparativas.
    """
    # Mapeia máscaras disponíveis
    mascaras = sorted(list(mask_dir.rglob("*.png")))
    if not mascaras:
        print(f"❌ Nenhuma máscara encontrada em '{mask_dir}'.")
        print("Execute primeiro: python ml/scripts/generate_masks.py")
        return

    # Separa por classe (Fire e No Fire)
    mascaras_por_classe: Dict[str, List[Path]] = {"Fire": [], "No Fire": []}
    for m in mascaras:
        if "no fire" in str(m).lower() or "nofire" in str(m).lower():
            mascaras_por_classe["No Fire"].append(m)
        else:
            mascaras_por_classe["Fire"].append(m)

    print(f"\n🔍 Máscaras localizadas: {len(mascaras)} total "
          f"({len(mascaras_por_classe['Fire'])} Fire, {len(mascaras_por_classe['No Fire'])} No Fire)")
    print(f"🖼️  Backend de renderização: {'Matplotlib (figura acadêmica)' if HAS_MATPLOTLIB else 'Pillow/NumPy (nativo)'}")
    print(f"📁 Destino das visualizações: {output_dir}\n")

    output_dir.mkdir(parents=True, exist_ok=True)
    total_geradas = 0

    for cls in ["Fire", "No Fire"]:
        amostras_cls = mascaras_por_classe[cls]
        # Se for Fire, seleciona algumas com maior presença de fogo
        amostras_selecionadas = amostras_cls[:num_samples]

        print(f"--- Gerando visualizações para a classe '{cls}' ({len(amostras_selecionadas)} amostras) ---")
        for m_path in amostras_selecionadas:
            # Encontrar o TIFF original correspondente
            stem = m_path.stem
            tiffs_candidatos = list(data_dir.rglob(f"{stem}.tif")) + list(data_dir.rglob(f"{stem}.tiff"))
            if not tiffs_candidatos:
                # Tenta busca parcial pelo stem
                tiffs_candidatos = list(data_dir.rglob(f"*{stem}*.tif")) + list(data_dir.rglob(f"*{stem}*.tiff"))

            if not tiffs_candidatos:
                print(f"  ⚠️ TIFF correspondente a '{m_path.name}' não encontrado em {data_dir}. Pulando...")
                continue

            tiff_path = tiffs_candidatos[0]

            # Carrega dados
            try:
                matriz_temp = carregar_tiff_temperatura(tiff_path)
                mascara_bin = carregar_mascara_binaria(m_path)
            except Exception as e:
                print(f"  ❌ Erro ao ler TIFF/Máscara para '{stem}': {e}")
                continue

            # Localiza o RGB corrigido
            rgb_path = encontrar_rgb_corrigido(tiff_path, data_dir)
            if rgb_path and rgb_path.exists():
                try:
                    img_rgb = np.array(Image.open(str(rgb_path)).convert("RGB"))
                    # Garante resolução idêntica se houver divergência sutil
                    if img_rgb.shape[:2] != matriz_temp.shape[:2]:
                        img_pil = Image.fromarray(img_rgb).resize((matriz_temp.shape[1], matriz_temp.shape[0]))
                        img_rgb = np.array(img_pil)
                except Exception:
                    img_rgb = np.zeros((*matriz_temp.shape, 3), dtype=np.uint8)
            else:
                # Se não encontrar o RGB correspondente, usa uma base neutra ou o próprio mapa térmico
                img_rgb = aplicar_colormap_termico_pil(matriz_temp)

            # Gera sobreposição
            overlay = criar_sobreposicao(img_rgb, mascara_bin, alpha=alpha)

            t_min = float(np.nanmin(matriz_temp))
            t_max = float(np.nanmax(matriz_temp))
            total_px = mascara_bin.size
            fogo_px = int(np.sum(mascara_bin > 0))
            pct_fogo = (fogo_px / total_px) * 100.0

            nome_saida = f"overlay_{cls.lower().replace(' ', '_')}_{stem}.png"
            caminho_final = output_dir / nome_saida

            if HAS_MATPLOTLIB:
                renderizar_painel_matplotlib(
                    caminho_saida=caminho_final,
                    nome_amostra=stem,
                    rgb_img=img_rgb,
                    matriz_temp=matriz_temp,
                    mascara=mascara_bin,
                    overlay=overlay,
                    temp_min=t_min,
                    temp_max=t_max,
                    pct_fogo=pct_fogo,
                    limiar=threshold
                )
            else:
                renderizar_painel_pil(
                    caminho_saida=caminho_final,
                    nome_amostra=stem,
                    rgb_img=img_rgb,
                    matriz_temp=matriz_temp,
                    mascara=mascara_bin,
                    overlay=overlay,
                    temp_min=t_min,
                    temp_max=t_max,
                    pct_fogo=pct_fogo,
                    limiar=threshold
                )

            print(f"  ✅ Painel gerado: {nome_saida} (T_max: {t_max:.1f} °C, Fogo: {pct_fogo:.2f}%)")
            total_geradas += 1

    print("\n" + "=" * 80)
    print(f"🏁 Finalizado! {total_geradas} painéis visuais salvos em: {output_dir}")
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
        default=5,
        help="Quantidade de amostras a visualizar por classe (padrão: 5)."
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

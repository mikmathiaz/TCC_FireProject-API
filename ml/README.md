# Fire Watcher — Módulo de Machine Learning (FLAME 3) 🛰️🔥

Este módulo contém a infraestrutura e os scripts para o treinamento e avaliação de modelos de **Visão Computacional para Segmentação Semântica de Fogo** baseados no dataset **FLAME 3** (drone DJI M30T, Sycan Marsh, Oregon).

---

## 🏛️ 1. Estrutura do Módulo `ml/`

```text
ml/
├── requirements-ml.txt        # Dependências exclusivas do pipeline de ML
├── README.md                  # Este guia metodológico e operacional
├── scripts/
│   ├── inspect_dataset.py     # Inspeção da árvore, contagem de classes e estatísticas dos TIFFs
│   ├── generate_masks.py      # Geração de ground truth binário (TIFF >= 80 °C -> PNG)
│   └── visualize_masks.py     # Geração de painéis de conferência (RGB + Térmico + Máscara + Overlay)
├── data/                      # Diretório local para o dataset e máscaras (ignorado no git)
│   ├── CVSubset/              # Amostras do FLAME 3 (Fire e No Fire)
│   └── masks/                 # Máscaras binárias PNG e masks_metadata.csv
└── outputs/                   # Saídas visuais e logs (ignorado no git)
    └── visualizations/        # Painéis de conferência com sobreposição
```

---

## 📐 2. Fundamentação Teórica para a Defesa do TCC

1. **Por que Sensoriamento com Câmera Térmica Radiométrica (TIFF em °C)?**
   - Sensores RGB convencionais sofrem com saturação luminosa, reflexos solares e obscurecimento por fumaça espessa.
   - O sensor radiométrico do DJI M30T capta ondas longas no infravermelho termal (LWIR), gravando a temperatura física absoluta de cada pixel em graus Celsius.
2. **Por que o Limiar de 80.0 °C para a Máscara Ground Truth?**
   - Em queimadas florestais em biomas secos, o solo exposto sob radiação solar direta atinge rotineiramente entre 45 °C e 60 °C.
   - Adotar um limiar conservador de $\ge 80^\circ\text{C}$ separa de forma inequívoca o aquecimento passivo do solo da combustão ativa e brasas incandescentes (*smoldering*).
3. **Por que Divisão em Blocos Contíguos de Tempo (Não Aleatória)?**
   - Imagens consecutivas capturadas por drones em voo apresentam correlação espacial e temporal extrema (quase idênticas).
   - Um *split* aleatório (*random train/test split*) causaria vazamento de dados (*data leakage* severo), inflando artificialmente as métricas de acurácia. A divisão deve ser realizada em blocos contínuos no tempo.
4. **Por que Perda Combinada (BCE + Dice)?**
   - Em imagens aéreas de incêndios, os pixels de fogo representam tipicamente menos de 1% a 5% da imagem (forte desbalanceamento de classes).
   - A *Cross-Entropy* padrão foca excessivamente no fundo (classe majoritária), enquanto a *Dice Loss* otimiza diretamente a sobreposição das regiões de fogo.

---

## 🚀 3. Instruções de Execução (Etapa 1)

### Passo 1: Instalar as Dependências de ML
```bash
pip install -r ml/requirements-ml.txt
```

### Passo 2: Inspecionar o Dataset
```bash
python ml/scripts/inspect_dataset.py --data-dir ml/data/CVSubset --threshold 80.0
```

### Passo 3: Gerar as Máscaras Binárias a partir dos TIFFs
```bash
python ml/scripts/generate_masks.py --data-dir ml/data/CVSubset --output-dir ml/data/masks --threshold 80.0
```

### Passo 4: Conferir Visualmente as Sobreposições
```bash
python ml/scripts/visualize_masks.py --data-dir ml/data/CVSubset --mask-dir ml/data/masks --output-dir ml/outputs/visualizations --num-samples 5
```

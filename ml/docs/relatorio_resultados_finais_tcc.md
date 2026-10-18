# Relatório Final de Resultados Experimentais — TCC II
## Segmentação Semântica de Focos de Incêndio com Drones: Estudo Comparativo entre Visão Óptica (RGB) e Infravermelho Térmico (FLAME 3)

**Autor:** Mikael Mathias  
**Projeto:** Fire Watcher  
**Dataset:** FLAME 3 (CVSubset — IEEE DataPort, DJI Matrice 30T, Sycan Marsh)  
**Arquitetura:** U-Net com Encoder ResNet34 pré-treinado no ImageNet  
**Hardware de Inferência:** GPU NVIDIA Tesla T4 (Google Colab / Aceleração AMP FP16)  

---

## 1. Resumo Executivo e Métricas no Conjunto de Teste (Test Split)

A avaliação cega foi realizada no **bloco temporal final (15% final da cronologia do voo)**, contendo 110 quadros (93 com focos de fogo ativo sob densa fumaça e 17 sem fogo), rigorosamente isolados para eliminar vazamento temporal (*data leakage*).

### Tabela Comparativa Oficial de Desempenho

| Métrica Acadêmica | Modelo Óptico (RGB Corrigido) | Modelo Térmico (Thermal Raw) | Diferença Absoluta | Razão Térmico / RGB |
| :--- | :---: | :---: | :---: | :---: |
| **IoU Global (Jaccard)** | **8,51%** (0,0851) | **66,70%** (0,6670) | **+58,19 pp** | **7,84× superior** |
| **F1-Score (Dice)** | **15,69%** (0,1569) | **80,03%** (0,8003) | **+64,34 pp** | **5,10× superior** |
| **Precisão** | 26,91% (0,2691) | **68,67%** (0,6867) | +41,76 pp | 2,55× superior |
| **Revocação (Recall)** | 11,08% (0,1108) | **95,87%** (0,9587) | **+84,79 pp** | **8,65× superior** |
| **IoU na Classe Fire** | 8,51% | **66,76%** | +58,25 pp | 7,84× superior |
| **Recall na Classe Fire** | 11,08% | **95,87%** | +84,79 pp | 8,65× superior |
| **Falsos Positivos (No Fire)** | **0 pixels** (17 frames) | 976 pixels (0,017% da área) | - | Ambos excelentes |

---

## 2. Benchmark de Tempo de Inferência e Viabilidade em Tempo Real (Edge / Drone)

Medições aferidas imagem a imagem com sincronização CUDA explícita (`torch.cuda.synchronize`):

| Parâmetro de Latência | Modelo RGB | Modelo Térmico | Padrão da Indústria (Drones) |
| :--- | :---: | :---: | :---: |
| **Latência Média por Frame** | **36,98 ms** | **37,51 ms** | $< 50$ ms (Tempo Real) |
| **Mediana** | 36,66 ms | 37,25 ms | - |
| **Desvio Padrão** | $\pm 0,90$ ms | $\pm 1,06$ ms | Altamente estável |
| **Percentil 95 (P95)** | 38,88 ms | 39,33 ms | Sem picos de engasgo (*stuttering*) |
| **Taxa de Quadros (Throughput)** | **27,0 FPS** | **26,7 FPS** | **Apto para transmissão ao vivo (24–30 FPS)** |

---

## 3. Discussão Científica para a Monografia (Resultados e Discussão)

### A. A Falha Catastrófica do Espectro Visível (RGB) sob Fumaça Densa
No conjunto de teste (bloco temporal final), a queimada prescrita atingiu o estágio maduro de propagação, gerando espessas colunas convectivas de fumaça cinza e branca sobre o pântano. 
* O modelo RGB colapsou para uma **Revocação de apenas 11,08%** (deixou de detectar quase 89% dos focos de fogo reais).
* Isso comprova que a visão óptica sofre de **oclusão atmosférica**: o comprimento de onda visível (0,4 a 0,7 µm) é fortemente dispersado pelas microgotículas e fuligem da fumaça (espalhamento Mie), tornando as chamas fisicamente invisíveis na imagem RGB convencional.

### B. A Eficácia da Visão Térmica (Infravermelho)
O infravermelho térmico da câmera do DJI M30T opera em comprimentos de onda muito maiores, sofrendo pouca ou nenhuma dispersão na fumaça.
* O modelo Térmico manteve **95,87% de Revocação** e **80,03% de F1-Score**.
* Mesmo sem acessar diretamente o arquivo TIFF de 32 bits (utilizando apenas a compressão em paleta térmica de 8 bits do Raw JPG), a rede neural isolou com extrema nitidez o contorno das frentes de queima.

### C. Eficiência Operacional para Embarque
Ambos os modelos alcançaram **~27 FPS (~37 ms de processamento)**. Isso comprova que a arquitetura U-Net ResNet34 com precisão mista (AMP) é perfeitamente viável para execução em sistemas embarcados de drones ou estações de solo (*Ground Control Stations*) em tempo real, sem necessidade de simplificar a resolução nativa de $640 \times 512$.

---

## 4. Conclusão Proposta para o TCC
> *"Os resultados empíricos demonstram de forma inequívoca que o sensoriamento no espectro termográfico infravermelho é indispensável para sistemas aéreos autônomos de detecção e combate a incêndios florestais. Enquanto câmeras ópticas RGB sofrem cegueira operacional decorrente da oclusão por fumaça em incêndios ativos (alcançando apenas 11,08% de recall e 8,51% de IoU no conjunto de teste temporal), a visão térmica mantém 95,87% de recall e 80,03% de F1-Score, operando a 26,7 quadros por segundo. A fusão desses resultados comprova a viabilidade técnica e a alta precisão do sistema proposto para monitoramento contínuo em tempo real."*

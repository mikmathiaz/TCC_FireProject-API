# Fire Watcher 🛰️🔥

> **Sistema de Monitoramento Inteligente e Detecção Precoce de Queimadas**  
> Trabalho de Conclusão de Curso (TCC II) — Bacharelado em Engenharia da Computação

---

## 📌 1. Visão Geral e Motivação Acadêmica

O monitoramento operacional oficial de queimadas no Brasil, conduzido principalmente pelo **Programa Queimadas do INPE (BDQueimadas)**, desempenha um papel essencial na vigilância ambiental do país. No entanto, os produtos operacionais mais frequentes (como os baseados nos sensores orbitais MODIS e VIIRS) apresentam duas limitações estruturais intrínsecas ao sensoriamento remoto de ampla cobertura:
1. **Resolução Espacial Grosseira:** Resoluções típicas entre 375 m e 1 km por pixel, o que dificulta a detecção de pequenos focos iniciais ou a caracterização fina da vegetação suscetível.
2. **Latência de Reporte:** Intervalos de revisita e processamento que podem atingir até 6 horas, período no qual um fogo florestal pode evoluir consideravelmente.

### Objetivo do Projeto
O **Fire Watcher** surge como uma **ferramenta complementar** (não substituta) ao BDQueimadas. O sistema processa dados orbitais de satélites com resolução espacial mais refinada (**Sentinel-2**, com bandas de 10 m e 20 m), calculando índices espectrais de vegetação e umidade para mapear zonas de risco elevado de ignição e propagação de queimadas em Áreas de Interesse (AOI), validando seus resultados com a base histórica de focos de calor do próprio INPE.

---

## 📐 2. Fundamentação Teórica — Índices Espectrais

O sistema avalia a suscetibilidade à queima por meio de quatro índices biofísicos calculados sobre as bandas do sensor MSI (*MultiSpectral Instrument*) do satélite Sentinel-2:

| Índice | Nome | Bandas Utilizadas | Fórmula | Significado Biofísico / Relevância no TCC |
| :--- | :--- | :--- | :--- | :--- |
| **NDVI** | *Normalized Difference Vegetation Index* | $B8$ (NIR) e $B4$ (Red) | $\frac{B8 - B4}{B8 + B4}$ | Vigor e densidade da cobertura vegetal. Quedas no NDVI indicam vegetação rala, ressecada ou sob estresse. |
| **NBR** | *Normalized Burn Ratio* | $B8$ (NIR) e $B12$ (SWIR 2) | $\frac{B8 - B12}{B8 + B12}$ | Sensível ao conteúdo de umidade e à estrutura das folhas. Valores baixos apontam solo seco e cicatrizes de queima. |
| **NDII** | *Normalized Difference Infrared Index* | $B8$ (NIR) e $B11$ (SWIR 1) | $\frac{B8 - B11}{B8 + B11}$ | Mede o estresse hídrico e o conteúdo de água na copa da vegetação (*canopy water content*). |
| **PSRI** | *Plant Senescence Reflectance Index* | $B4$ (Red), $B2$ (Blue), $B8$ (NIR) | $\frac{B4 - B2}{B8}$ | Avalia o nível de senescência (envelhecimento/desidratação) da planta pela relação caroteno/clorofila. Altos valores indicam biomassa seca altamente combustível. |

---

## 🏛️ 3. Arquitetura do Sistema

O projeto é estruturado em três camadas modulares:

```
fire-watcher/
├── backend/                  # Servidor de processamento e API REST (FastAPI)
│   ├── app/
│   │   ├── api/endpoints/    # Rotas da API (análise, validação INPE, clima, configuração)
│   │   ├── core/             # Configurações de ambiente e conexão com banco SQLite
│   │   ├── models/           # Entidades e tabelas do banco de dados (SQLAlchemy)
│   │   ├── schemas/          # Modelos de validação de entrada/saída (Pydantic)
│   │   ├── services/         # Regras de negócio, cálculo de índices e integrações
│   │   └── main.py           # Ponto de entrada FastAPI
│   └── tests/                # Testes unitários automatizados (pytest)
├── frontend/                 # Painel interativo para o usuário e banca (Streamlit)
│   ├── pages/                # Telas da aplicação (Dashboard, Detalhes, Histórico, Configurações)
│   ├── components/           # Componentes visuais reutilizáveis (mapas com Folium, gráficos)
│   ├── services/             # Comunicação HTTP com o backend FastAPI
│   └── app.py                # Ponto de entrada Streamlit
├── data/                     # Armazenamento local (SQLite e amostras do INPE)
├── docs/                     # Diagramas UML, notas metodológicas e documentação do TCC
├── requirements.txt          # Dependências do projeto
├── .env.example              # Modelo de variáveis de ambiente
└── README.md                 # Documento principal
```

---

## 🚀 4. Instalação e Execução Local

### Pré-requisitos
- **Python 3.10+** (recomendado Python 3.11 ou 3.12/3.13)
- **Git** instalado

### Passo 1: Criar e ativar o ambiente virtual (venv)
No terminal do projeto (`fire-watcher`):

```bash
# Criar o ambiente virtual isolado
python -m venv .venv

# Ativar no Windows (PowerShell):
.venv\Scripts\Activate.ps1

# (Ou no Linux / macOS):
# source .venv/bin/activate
```

### Passo 2: Instalar as dependências
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 3: Configurar variáveis de ambiente
Copie o arquivo de exemplo para `.env`:
```bash
cp .env.example .env
```

### Passo 4: Executar o Backend (FastAPI)
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Documentação interativa Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Especificação Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Passo 5: Executar o Frontend (Streamlit)
Em um novo terminal (com o ambiente virtual ativo):
```bash
streamlit run frontend/app.py
```
- Acesse a interface web em: [http://localhost:8501](http://localhost:8501)

---

## 🧪 5. Execução de Testes Automatizados

Para validar o cálculo correto dos índices e a classificação de risco:
```bash
pytest backend/tests/ -v
```

---

## 📦 6. Publicação e Controle de Versão (GitHub)

Para subir o projeto no GitHub pela primeira vez:

1. Crie um novo repositório vazio no GitHub (ex: `fire-watcher`). Não selecione "Add README" nem ".gitignore".
2. No terminal do projeto, execute:
```bash
# Inicializar o repositório local
git init

# Adicionar todos os arquivos rastreados
git add .

# Realizar o primeiro commit
git commit -m "feat: estrutura inicial do projeto e documentação acadêmica"

# Definir a branch principal como main
git branch -M main

# Conectar ao repositório remoto do GitHub (substitua pelo seu link)
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git

# Enviar os arquivos para o GitHub
git push -u origin main
```

---

## 📚 7. Referências e Créditos
- **INPE — Instituto Nacional de Pesquisas Espaciais:** Programa Queimadas (BDQueimadas).
- **ESA — European Space Agency:** Missão Sentinel-2 / Copernicus Open Access Hub.
- **Open-Meteo:** Historical & Forecast Weather API.

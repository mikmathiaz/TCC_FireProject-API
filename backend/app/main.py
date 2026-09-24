"""
Aplicação Principal FastAPI — Fire Watcher Backend
Ponto de entrada do servidor de processamento e API REST.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import Base, engine
from backend.app.api.endpoints import config_aoi, analysis, validation, weather

# Inicialização automática das tabelas SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Habilitar CORS para permitir requisições do frontend Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos roteadores de endpoints
app.include_router(config_aoi.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(validation.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")


@app.get("/", tags=["Healthcheck"])
def healthcheck():
    """
    Endpoint de verificação de integridade da API.
    """
    return {
        "status": "online",
        "projeto": settings.API_TITLE,
        "versao": settings.API_VERSION,
        "ambiente": settings.ENVIRONMENT,
        "documentacao": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)

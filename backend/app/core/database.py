"""
Gerenciamento de conexão com o banco de dados SQLite via SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

# Para SQLite, 'check_same_thread': False é necessário para FastAPI lidar com múltiplas threads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency generator para injeção de dependência da sessão de banco no FastAPI.
    Garante fechamento correto da sessão após a requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

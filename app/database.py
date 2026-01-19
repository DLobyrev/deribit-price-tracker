"""
Подключение к PostgreSQL через SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Формат: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/deribit_db"
)

# Создаём движок SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)  # echo=True — для отладки SQL

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Dependency для FastAPI: даёт сессию БД и закрывает её после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
Адаптер для работы с базой данных в контексте Airflow
Совместимость с SQLAlchemy 1.4.x
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# Создаем асинхронный движок
async_engine = create_async_engine(
    settings.db.dsn,
    echo=False,
    future=True
)

# Создаем фабрику сессий для SQLAlchemy 1.4
async_session_maker = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

__all__ = ["async_session_maker", "async_engine"]
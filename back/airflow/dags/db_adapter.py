"""
Адаптер для работы с базой данных в контексте Airflow
Совместимость с SQLAlchemy 1.4.x
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Настройки для подключения к БД
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'levelupper')
DB_USER = os.getenv('DB_USER', 'dallenal')
DB_PASSWORD = os.getenv('DB_PASSWORD', '1xOsgTgZf')
DB_PORT = os.getenv('DB_PORT', '5432')

# Формируем DSN для подключения
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем асинхронный движок
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Отключаем логи SQL в Airflow
    future=True
)

# Создаем фабрику сессий для SQLAlchemy 1.4
async_session_maker = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

__all__ = ["async_session_maker", "async_engine"]
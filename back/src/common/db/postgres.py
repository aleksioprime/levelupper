from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.common.core.config import settings

engine = create_async_engine(
    settings.db.dsn,
    echo=settings.db.show_query,
    future=True,
    )

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей"""
    pass


async def get_db_session() -> AsyncSession:
    """
    Получение асинхронной сессии базы данных
    """
    async with async_session_maker() as session:
        yield session
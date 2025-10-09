import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Получаем настройки из переменных окружения
DB_NAME = os.getenv('DB_NAME', 'database')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', '1q2w3e')
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
SHOW_SQL_QUERY = os.getenv('SHOW_SQL_QUERY', 'false').lower() == 'true'

# Формируем DSN
dsn = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(dsn, echo=SHOW_SQL_QUERY, future=True)

# Для совместимости с разными версиями SQLAlchemy
try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
except ImportError:
    # Для старых версий SQLAlchemy
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

Base = declarative_base()


async def get_db_session() -> AsyncSession:
    """
    Получение асинхронной сессии базы данных
    """
    async with async_session_maker() as session:
        yield session

import uvicorn
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src.common.db import redis
from src.common.core.config import settings
from src.common.core.logger import LOGGING
from src.common.api import ping
from src.common.exceptions.handlers import register_exception_handlers
from src.common.elasticsearch import init_elasticsearch, close_elasticsearch

from src.auth.presentation import router as auth_router
from src.courses.presentation import router as course_router
from src.admin import create_admin_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения FastAPI.
    Создает подключения к Redis и Elasticsearch при старте приложения и закрывает их при завершении.
    """
    # Инициализация Redis
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)

    # Инициализация Elasticsearch
    await init_elasticsearch()

    yield

    # Закрытие соединений
    await redis.redis.close()
    await close_elasticsearch()


# Инициализация FastAPI-приложения
app = FastAPI(
    lifespan=lifespan, # Указание жизненного цикла приложения
    version="0.0.1", # Версия приложения
    title=settings.project_name, # Название приложения
    description=settings.project_description, # Описание приложения
    docs_url="/api/openapi", # URL для документации Swagger
    openapi_url="/api/openapi.json", # URL для OpenAPI схемы
    default_response_class=ORJSONResponse, # Быстрая обработка JSON с ORJSON
)

# Регистрация обработчиков исключений
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,  # Разрешить Vue.js
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)


# Подключение роутера для проверки доступности сервера
app.include_router(ping.router, prefix="/api/v1", tags=["ping"])
# Подключение роутера для работы с авторизацией
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
# Подключение роутера для работы с курсами
app.include_router(course_router, prefix="/api/v1", tags=["courses"])

# Подключение админ-панели SQLAdmin
admin = create_admin_app(app)


# Точка входа в приложение
if __name__ == "__main__":
    # Запуск Uvicorn-сервера
    uvicorn.run(
        "src.main:app",  # Указание приложения (main.py:app)
        host=settings.default_host,  # Хост из настроек
        port=settings.default_port,  # Порт из настроек
        log_config=LOGGING,  # Конфигурация логирования
        log_level=logging.INFO,  # Уровень логирования
        reload=True,  # Автоматическая перезагрузка при изменении файлов
    )
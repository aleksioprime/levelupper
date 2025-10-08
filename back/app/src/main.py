import uvicorn
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis

from src.db import redis
from src.core.config import settings
from src.core.logger import LOGGING
from src.api.v1 import router
from src.exceptions.handlers import register_exception_handlers
from src.admin import setup_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения FastAPI.
    Создает подключение к Redis при старте приложения и закрывает его при завершении
    """
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
    yield
    await redis.redis.close()


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

# Настройка CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,  # Разрешить Vue.js
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

# Настройка статических файлов (например, для хранения медиафайлов)
os.makedirs(settings.media.photo_path, exist_ok=True)
app.mount(settings.media.photo_url, StaticFiles(directory=settings.media.photo_path), name="media")

# Подключение роутера для версии v1
app.include_router(router, prefix="/api/v1")

# Инициализация и подключение административной панели SQLAdmin
setup_admin(app)

# Точка входа в приложение
if __name__ == "__main__":
    # Запуск Uvicorn-сервера
    uvicorn.run(
        "src.main:app",  # Указание приложения (src.main:app)
        host=settings.default_host,  # Хост из настроек
        port=settings.default_port,  # Порт из настроек
        log_config=LOGGING,  # Конфигурация логирования
        log_level=logging.INFO,  # Уровень логирования
        reload=True,  # Автоматическая перезагрузка при изменении файлов
    )
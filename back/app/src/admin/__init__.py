"""
Инициализация SQLAdmin административной панели для микросервисной архитектуры
"""
from sqladmin import Admin
from fastapi import FastAPI

from src.core.config import settings
from src.db.postgres import async_session_maker
from .auth import AdminAuth
from .client import AuthServiceClient
from .models import setup_admin_views


def setup_admin(app: FastAPI) -> Admin:
    """
    Создаёт и регистрирует SQLAdmin для приложения.

    Особенности для микросервисной архитектуры:
    - Аутентификация через auth-сервис
    - Обогащение данных пользователями через HTTP API
    - Кэширование токенов в сессии

    Returns:
        Admin: Инстанс админки для дополнительной настройки
    """

    admin = Admin(
        app,
        session_maker=async_session_maker,
        base_url="/admin",
        authentication_backend=AdminAuth(secret_key=settings.jwt.secret_key),
        title="LevelUpper Admin",
        logo_url=None,  # Можно добавить логотип
    )

    # Регистрируем все представления моделей
    setup_admin_views(admin)

    return admin


__all__ = ["setup_admin", "AdminAuth", "AuthServiceClient"]

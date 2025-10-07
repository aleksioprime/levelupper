"""
Инициализация SQLAdmin административной панели
"""
from sqladmin import Admin
from fastapi import FastAPI

from src.core.config import settings
from src.db.postgres import async_session_maker
from .auth import AdminAuth
from .models import setup_admin_views


def setup_admin(app: FastAPI) -> AdminAuth:
    """Создаёт и регистрирует SQLAdmin для приложения.
    Возвращает инстанс Admin, чтобы при необходимости можно было донастроить его снаружи.
    """

    admin = Admin(
        app,
        session_maker=async_session_maker,
        base_url="/admin",
        authentication_backend=AdminAuth(secret_key=settings.jwt.secret_key),
    )
    setup_admin_views(admin)
    return admin


__all__ = ["setup_admin"]

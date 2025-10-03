"""
Инициализация SQLAdmin административной панели.

Аутентификация для входа в админку и регистрация вьюх.
"""

import uuid
from typing import Optional

from fastapi import FastAPI
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select, or_
from starlette.requests import Request

from src.common.db.postgres import async_session_maker
from .models import setup_admin_views

# Константы
ADMIN_SESSION_DURATION = 8 * 3600  # 8 часов в секундах
ADMIN_SESSION_PREFIX = "admin_session:"


def _get_redis():
    """Получаем Redis безопасно."""
    try:
        from src.common.db.redis import redis
        return redis
    except (ImportError, AttributeError):
        return None


class AdminAuth(AuthenticationBackend):
    """Простой backend аутентификации для SQLAdmin.

    - Логин по username или email + паролю.
    - В админку пускаем только superuser.
    - Состояние сохраняется в Redis для надежности.
    """

    async def login(self, request: Request) -> bool:  # type: ignore[override]
        """Аутентификация пользователя в админке."""
        form = await request.form()
        username_or_email = (form.get("username") or "").strip()
        password = (form.get("password") or "").strip()

        if not username_or_email or not password:
            return False

        # Импорт здесь, чтобы избежать циклических зависимостей
        from src.auth.infrastructure.persistence.sqlalchemy.models.user import User

        async with async_session_maker() as session:
            user = await session.scalar(
                select(User).where(
                    or_(User.username == username_or_email, User.email == username_or_email)
                )
            )

            if not user or not user.check_password(password) or not getattr(user, "is_superuser", False):
                return False

            # Сохраняем данные в сессии
            session_data = {
                "admin_user_id": str(user.id),
                "admin_authenticated": True
            }

            # Пытаемся сохранить в Redis для надежности
            redis_client = _get_redis()
            if redis_client:
                try:
                    session_token = str(uuid.uuid4())
                    await redis_client.set(
                        f"{ADMIN_SESSION_PREFIX}{session_token}",
                        str(user.id),
                        ex=ADMIN_SESSION_DURATION
                    )
                    session_data["admin_session_token"] = session_token
                except Exception:
                    # Если Redis недоступен, продолжаем без него
                    pass

            request.session.update(session_data)
            return True

    async def logout(self, request: Request) -> bool:  # type: ignore[override]
        """Выход из админки."""
        session_token = request.session.get("admin_session_token")
        if session_token:
            redis_client = _get_redis()
            if redis_client:
                try:
                    await redis_client.delete(f"{ADMIN_SESSION_PREFIX}{session_token}")
                except Exception:
                    pass  # Игнорируем ошибки Redis при logout

        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:  # type: ignore[override]
        """Проверка аутентификации для каждого запроса к админке."""
        # Сначала проверяем обычную сессию
        if request.session.get("admin_authenticated") and request.session.get("admin_user_id"):
            return True

        # Затем проверяем Redis если есть токен
        session_token = request.session.get("admin_session_token")
        if session_token:
            redis_client = _get_redis()
            if redis_client:
                try:
                    user_id = await redis_client.get(f"{ADMIN_SESSION_PREFIX}{session_token}")
                    if user_id:
                        return True
                except Exception:
                    pass  # Игнорируем ошибки Redis

            # Если токен не найден в Redis, очищаем его из сессии
            request.session.pop("admin_session_token", None)

        return False

def setup_admin(app: FastAPI) -> Admin:
    """Создаёт и регистрирует SQLAdmin для приложения.

    Возвращает инстанс Admin, чтобы при необходимости можно было донастроить его снаружи.
    """
    from src.common.core.config import settings

    admin = Admin(
        app,
        session_maker=async_session_maker,
        base_url="/admin",
        # Используем тот же secret_key что и для SessionMiddleware
        authentication_backend=AdminAuth(secret_key=settings.jwt.secret_key),
    )
    setup_admin_views(admin)
    return admin


__all__ = ["setup_admin"]

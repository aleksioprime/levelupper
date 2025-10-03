"""
Инициализация SQLAdmin административной панели.

Здесь описана аутентификация для входа в админку и регистрация вьюх.
"""

from fastapi import FastAPI
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select, or_
from starlette.requests import Request

from src.common.db.postgres import engine, async_session_maker
from .models import setup_admin_views


class AdminAuth(AuthenticationBackend):
    """Простой backend аутентификации для SQLAdmin.

    - Логин по username или email + паролю.
    - В админку пускаем только superuser.
    - Состояние сохраняется в session.
    """

    session_key_user_id = "admin_user_id"
    session_key_is_superuser = "admin_is_superuser"

    async def login(self, request: Request) -> bool:  # type: ignore[override]
        form = await request.form()
        username_or_email = (form.get("username") or "").strip()
        password = (form.get("password") or "").strip()

        if not username_or_email or not password:
            return False

        # Импорт здесь, чтобы избежать циклических зависимостей при инициализации
        from src.auth.infrastructure.persistence.sqlalchemy.models.user import User

        async with async_session_maker() as session:
            user = await session.scalar(
                select(User).where(
                    or_(User.username == username_or_email, User.email == username_or_email)
                )
            )

            if not user:
                return False

            if not user.check_password(password):
                return False

            if not getattr(user, "is_superuser", False):
                return False

            request.session.update({
                self.session_key_user_id: str(user.id),
                self.session_key_is_superuser: True,
            })
            return True

    async def logout(self, request: Request) -> bool:  # type: ignore[override]
        request.session.clear()
        return True

    async def is_authenticated(self, request: Request) -> bool:  # type: ignore[override]
        return bool(request.session.get(self.session_key_is_superuser) is True)


def setup_admin(app: FastAPI) -> Admin:
    """Создаёт и регистрирует SQLAdmin для приложения.

    Возвращает инстанс Admin, чтобы при необходимости можно было донастроить его снаружи.
    """
    admin = Admin(
        app,
        engine=engine,
        base_url="/admin",
        authentication_backend=AdminAuth(secret_key="sqladmin"),  # secret_key обязателен по API, но для Session используется middleware
    )

    setup_admin_views(admin)
    return admin

__all__ = ["setup_admin"]
"""
Инициализация SQLAdmin административной панели.
"""

from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.common.db.postgres import engine
from .models import setup_admin_views


class AdminAuth(AuthenticationBackend):
    """Простая аутентификация для админ-панели."""

    async def login(self, request: Request) -> bool:
        """Процедура входа в админку."""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        # Простая проверка (в продакшене используйте более надежную аутентификацию)
        if username == "admin" and password == "admin123":
            request.session.update({"token": "authenticated"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        """Процедура выхода из админки."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Проверка аутентификации."""
        token = request.session.get("token")
        return token == "authenticated"


def create_admin_app(app):
    """Создание и настройка админ-панели."""

    # Создаем админ-панель
    admin = Admin(
        app=app,  # Привязываем к основному приложению
        engine=engine,
        authentication_backend=AdminAuth(secret_key="admin_secret_key_change_in_production"),
        title="Smart Learning Admin",
        logo_url="/static/logo.png",  # Опционально
    )

    # Регистрируем модели
    setup_admin_views(admin)

    return admin
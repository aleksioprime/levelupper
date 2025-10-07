"""
Аутентификация для административной панели с использованием SQLAdmin
"""
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select

from src.db.postgres import async_session_maker
from src.models.user import User


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        """
        Аутентифицирует пользователя для доступа к админке.
        Проверяет логин/пароль и права супер-пользователя
        """
        form = await request.form()
        username_or_email = (form.get("username") or "").strip()
        password = (form.get("password") or "").strip()

        if not username_or_email or not password:
            return False

        try:
            async with async_session_maker() as session:
                # Ищем пользователя по username или email
                query = select(User).where(
                    (User.username == username_or_email) |
                    (User.email == username_or_email)
                )
                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user:
                    return False

                # Проверяем пароль и права супер-пользователя
                if not user.check_password(password):
                    return False

                if not user.is_superuser:
                    return False

                if not user.is_active:
                    return False

                # Сохраняем информацию о пользователе в сессии
                request.session.update({
                    "user_id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser
                })

                return True

        except Exception as e:
            # Логирование ошибки может быть добавлено здесь
            return False

    async def logout(self, request: Request) -> bool:
        """
        Очищает сессию пользователя при выходе из админки
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        """
        Проверяет аутентификацию пользователя для каждого запроса к админке
        """
        user_id = request.session.get("user_id")
        if not user_id:
            return None

        try:
            async with async_session_maker() as session:
                query = select(User).where(User.id == user_id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user or not user.is_superuser or not user.is_active:
                    return None

                # Возвращаем информацию о пользователе
                return {
                    "user_id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser
                }

        except Exception:
            return None
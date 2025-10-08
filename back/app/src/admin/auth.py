"""
Аутентификация для административной панели
"""
import logging
from typing import Optional, Dict

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from .client import AuthServiceClient

logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    """
    Аутентификация админки через auth-сервис
    """

    def __init__(self, secret_key: str):
        super().__init__(secret_key)
        self.auth_client = AuthServiceClient()

    async def login(self, request: Request) -> bool:
        """
        Аутентифицирует пользователя через auth-сервис
        """
        form = await request.form()
        username_or_email = (form.get("username") or "").strip()
        password = (form.get("password") or "").strip()

        if not username_or_email or not password:
            return False

        # Аутентификация через auth-сервис
        user_data = await self.auth_client.authenticate_user(username_or_email, password)

        if not user_data:
            return False

        # Сохраняем информацию о пользователе в сессии
        self._update_session(request, user_data)
        return True

    async def logout(self, request: Request) -> bool:
        """
        Очищает сессию пользователя
        """
        access_token = request.session.get("access_token")
        if access_token:
            # Пытаемся выйти из auth-сервиса
            await self.auth_client.logout_user(access_token)

        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[Dict]:
        """
        Проверяет аутентификацию для каждого запроса
        """
        user_id = request.session.get("user_id")
        access_token = request.session.get("access_token")

        if not user_id:
            return None

        # Если есть токен, проверяем его валидность
        if access_token:
            user_data = await self._verify_token_and_update_session(request, access_token)
            if user_data:
                return user_data

        # Если токена нет или он невалиден, проверяем по user_id
        return await self._verify_user_by_id(request, user_id)

    def _update_session(self, request: Request, user_data: Dict) -> None:
        """
        Обновляет данные сессии пользователя
        """
        request.session.update({
            "user_id": str(user_data["id"]),
            "username": user_data.get("username", ""),
            "email": user_data.get("email", ""),
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", ""),
            "is_superuser": user_data.get("is_superuser", False),
            "access_token": user_data.get("access_token")
        })

    async def _verify_token_and_update_session(self, request: Request, access_token: str) -> Optional[Dict]:
        """
        Проверяет токен и обновляет данные сессии
        """
        try:
            user_data = await self.auth_client.verify_token(access_token)
            if user_data:
                # Обновляем данные сессии без токена (он уже есть)
                session_data = {k: v for k, v in user_data.items() if k != "access_token"}
                request.session.update(session_data)
                return user_data
            else:
                # Токен невалиден или пользователь не имеет прав
                request.session.clear()
                return None
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            request.session.clear()
            return None

    async def _verify_user_by_id(self, request: Request, user_id: str) -> Optional[Dict]:
        """
        Проверяет пользователя по ID
        """
        try:
            user_data = await self.auth_client.get_user_info(user_id)
            if user_data:
                return user_data
            else:
                # Пользователь больше не существует или не имеет прав
                request.session.clear()
                return None
        except Exception as e:
            logger.warning(f"User verification failed: {e}")
            request.session.clear()
            return None
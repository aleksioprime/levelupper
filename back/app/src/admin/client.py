"""
Клиент для взаимодействия с auth-сервисом
"""
import logging
from typing import Dict, Optional

import httpx

from src.core.config import settings
from src.utils.token import JWTHelper

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """Клиент для взаимодействия с auth-сервисом"""

    def __init__(self):
        self.auth_url = settings.auth_service.url
        self.timeout = settings.auth_service.timeout
        self.jwt_helper = JWTHelper()

    async def authenticate_user(self, username_or_email: str, password: str) -> Optional[Dict]:
        """
        Аутентифицирует пользователя через auth-сервис
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Authenticating user: {username_or_email}. Auth URL: {self.auth_url}/api/v1/auth/login")

                response = await client.post(
                    f"{self.auth_url}/api/v1/auth/login/",
                    json={
                        "username": username_or_email,
                        "password": password
                    }
                )

                logger.info(f"Response status code: {response.status_code}")

                if response.status_code == 200:
                    auth_data = response.json()

                    # Получаем токены из ответа аутентификации
                    access_token = auth_data.get("access_token")
                    if not access_token:
                        logger.warning("No access_token in auth response")
                        return None

                    # Проверяем и получаем информацию о пользователе
                    user_data = await self._get_user_from_token(access_token)
                    if not user_data:
                        return None

                    # Добавляем токены к информации о пользователе
                    user_data.update({
                        "access_token": access_token,
                        "refresh_token": auth_data.get("refresh_token")
                    })

                    return user_data

                return None

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"Request to auth service failed: {e}")
            return None

    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        Проверяет JWT токен и получает информацию о пользователе
        """
        try:
            # Сначала проверяем токен локально
            token_data = self.jwt_helper.verify(token)
            user_id = token_data.get("sub")
            is_superuser = token_data.get("is_superuser", False)

            if not is_superuser:
                logger.info(f"User {user_id} is not a superuser")
                return None

            # Получаем актуальную информацию о пользователе через auth-сервис с токеном
            user_data = await self._get_user_info_from_auth_service(user_id, token)
            if not user_data:
                return None

            # Добавляем токен к информации о пользователе
            user_data["access_token"] = token
            return user_data

        except Exception as e:
            logger.warning(f"Failed to verify token: {e}")
            return None

    async def get_user_info(self, user_id: str, access_token: str) -> Optional[Dict]:
        """
        Получает информацию о пользователе по ID через auth-сервис
        """
        return await self._get_user_info_from_auth_service(user_id, access_token)

    async def logout_user(self, access_token: str) -> bool:
        """
        Выходит из системы через auth-сервис
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.auth_url}/api/v1/auth/logout",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Logout request failed: {e}")
            return False

    async def _get_user_from_token(self, access_token: str) -> Optional[Dict]:
        """
        Получает информацию о пользователе из токена и проверяет права суперпользователя
        """
        try:
            token_data = self.jwt_helper.verify(access_token)
            user_id = token_data.get("sub")
            is_superuser = token_data.get("is_superuser", False)

            if not is_superuser:
                logger.info(f"User {user_id} is not a superuser")
                return None

            # Получаем полную информацию о пользователе через auth-сервис с токеном
            return await self._get_user_info_from_auth_service(user_id, access_token)

        except Exception as e:
            logger.warning(f"Failed to get user from token: {e}")
            return None

    async def _get_user_info_from_auth_service(self, user_id: str, access_token: str) -> Optional[Dict]:
        """
        Получает информацию о пользователе через auth-сервис с JWT токеном
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_url}/api/v1/users/{user_id}/",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                if response.status_code == 200:
                    user_data = response.json()

                    # Проверяем права суперпользователя и активность
                    if not (user_data.get("is_superuser", False) and user_data.get("is_active", False)):
                        logger.info(f"User {user_id} is not an active superuser")
                        return None

                    return {
                        "id": user_data["id"],
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "first_name": user_data.get("first_name", ""),
                        "last_name": user_data.get("last_name", ""),
                        "is_superuser": user_data["is_superuser"],
                        "is_active": user_data["is_active"]
                    }
                elif response.status_code == 401:
                    logger.warning(f"Unauthorized access when getting user {user_id}")
                    return None
                elif response.status_code == 404:
                    logger.warning(f"User {user_id} not found in auth service")
                    return None
                else:
                    logger.error(f"Failed to get user info: {response.status_code}")
                    return None

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"Request to auth service failed: {e}")
            return None
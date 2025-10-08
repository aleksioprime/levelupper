"""Сервис для взаимодействия с auth-сервисом"""

from typing import Dict, List, Optional
import uuid
import httpx

from src.core.config import settings
from src.schemas.user import UserInfo


class AuthService:
    """Сервис для взаимодействия с auth-сервисом"""

    def __init__(self):
        # Используем настройки из конфига
        self.auth_service_url = settings.auth_service.url
        self.timeout = settings.auth_service.timeout

    async def get_user_info(self, user_id: uuid.UUID, user_token: Optional[str] = None) -> Optional[UserInfo]:
        """
        Получить информацию о пользователе по ID

        Args:
            user_id: ID пользователя
            user_token: Токен пользователя (если есть). Если не передан, используется service token
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = {}

                if user_token:
                    # Используем токен пользователя для точной авторизации
                    headers["Authorization"] = f"Bearer {user_token}"
                elif settings.auth_service.service_token:
                    # Fallback на service token для системных операций
                    headers["Authorization"] = f"Bearer {settings.auth_service.service_token}"

                response = await client.get(
                    f"{self.auth_service_url}/api/v1/users/{user_id}/",
                    headers=headers
                )
                if response.status_code == 200:
                    return UserInfo(**response.json())
                elif response.status_code == 404:
                    return None
                else:
                    response.raise_for_status()
            except httpx.RequestError:
                # Логируем ошибку и возвращаем None
                # В продакшене здесь должно быть логирование
                return None

    async def get_users_info(self, user_ids: List[uuid.UUID], user_token: Optional[str] = None) -> Dict[uuid.UUID, UserInfo]:
        """
        Получить информацию о нескольких пользователях

        Args:
            user_ids: Список ID пользователей
            user_token: Токен пользователя (если есть). Если не передан, используется service token
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = {}

                if user_token:
                    # Используем токен пользователя для точной авторизации
                    headers["Authorization"] = f"Bearer {user_token}"
                elif settings.auth_service.service_token:
                    # Fallback на service token для системных операций
                    headers["Authorization"] = f"Bearer {settings.auth_service.service_token}"

                response = await client.post(
                    f"{self.auth_service_url}/api/v1/users/batch/",
                    json={"user_ids": [str(uid) for uid in user_ids]},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    users_data = data.get("users", {})
                    return {
                        uuid.UUID(uid): UserInfo(**user_data)
                        for uid, user_data in users_data.items()
                    }
                else:
                    response.raise_for_status()
            except httpx.RequestError:
                # В случае ошибки возвращаем пустой словарь
                return {}

    async def verify_user_exists(self, user_id: uuid.UUID, user_token: Optional[str] = None) -> bool:
        """Проверить, существует ли пользователь"""
        user_info = await self.get_user_info(user_id, user_token)
        return user_info is not None

    # Convenience methods для ясности использования
    async def get_user_info_by_service(self, user_id: uuid.UUID) -> Optional[UserInfo]:
        """Получить информацию о пользователе через service token (системные операции)"""
        return await self.get_user_info(user_id, user_token=None)

    async def get_user_info_by_user(self, user_id: uuid.UUID, user_token: str) -> Optional[UserInfo]:
        """Получить информацию о пользователе через его токен (пользовательские операции)"""
        return await self.get_user_info(user_id, user_token=user_token)

    async def get_users_info_by_service(self, user_ids: List[uuid.UUID]) -> Dict[uuid.UUID, UserInfo]:
        """Получить информацию о нескольких пользователях через service token (системные операции)"""
        return await self.get_users_info(user_ids, user_token=None)

    async def get_users_info_by_user(self, user_ids: List[uuid.UUID], user_token: str) -> Dict[uuid.UUID, UserInfo]:
        """Получить информацию о нескольких пользователях через токен пользователя"""
        return await self.get_users_info(user_ids, user_token=user_token)


# Синглтон для использования в зависимостях
auth_service = AuthService()
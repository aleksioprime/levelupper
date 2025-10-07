"""Сервис для взаимодействия с auth-сервисом"""

from typing import Dict, List, Optional
import uuid
import httpx
from pydantic import BaseModel

from src.core.config import settings


class UserInfo(BaseModel):
    """Модель информации о пользователе из auth-сервиса"""
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_superuser: bool
    is_active: bool = True


class AuthService:
    """Сервис для взаимодействия с auth-сервисом"""

    def __init__(self):
        # URL должен быть в настройках
        self.auth_service_url = getattr(settings, 'AUTH_SERVICE_URL', 'http://auth:8000')
        self.timeout = 30.0

    async def get_user_info(self, user_id: uuid.UUID) -> Optional[UserInfo]:
        """Получить информацию о пользователе по ID"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.auth_service_url}/api/v1/users/{user_id}"
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

    async def get_users_info(self, user_ids: List[uuid.UUID]) -> Dict[uuid.UUID, UserInfo]:
        """Получить информацию о нескольких пользователях"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/users/batch",
                    json={"user_ids": [str(uid) for uid in user_ids]}
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        uuid.UUID(uid): UserInfo(**user_data)
                        for uid, user_data in data.items()
                    }
                else:
                    response.raise_for_status()
            except httpx.RequestError:
                # В случае ошибки возвращаем пустой словарь
                return {}

    async def verify_user_exists(self, user_id: uuid.UUID) -> bool:
        """Проверить, существует ли пользователь"""
        user_info = await self.get_user_info(user_id)
        return user_info is not None


# Синглтон для использования в зависимостях
auth_service = AuthService()
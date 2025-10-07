"""
Утилиты для админки
"""
import uuid
from typing import Dict, List, Optional
import httpx
from datetime import datetime

from src.core.config import settings


class UserCache:
    """Простой кэш для информации о пользователях"""

    def __init__(self, ttl: int = 300):  # 5 минут
        self._cache: Dict[str, Dict] = {}
        self._timestamps: Dict[str, datetime] = {}
        self.ttl = ttl

    def get(self, user_id: str) -> Optional[Dict]:
        """Получить пользователя из кэша"""
        if user_id not in self._cache:
            return None

        # Проверяем TTL
        if datetime.now().timestamp() - self._timestamps[user_id].timestamp() > self.ttl:
            self.remove(user_id)
            return None

        return self._cache[user_id]

    def set(self, user_id: str, user_data: Dict):
        """Сохранить пользователя в кэш"""
        self._cache[user_id] = user_data
        self._timestamps[user_id] = datetime.now()

    def remove(self, user_id: str):
        """Удалить пользователя из кэша"""
        self._cache.pop(user_id, None)
        self._timestamps.pop(user_id, None)

    def clear(self):
        """Очистить весь кэш"""
        self._cache.clear()
        self._timestamps.clear()


# Глобальный кэш пользователей
user_cache = UserCache()


async def get_users_info_cached(user_ids: List[str]) -> Dict[str, Dict]:
    """
    Получить информацию о пользователях с кэшированием
    """
    if not user_ids:
        return {}

    result = {}
    missing_ids = []

    # Проверяем кэш
    for user_id in user_ids:
        cached_user = user_cache.get(user_id)
        if cached_user:
            result[user_id] = cached_user
        else:
            missing_ids.append(user_id)

    # Запрашиваем недостающих пользователей
    if missing_ids:
        try:
            async with httpx.AsyncClient(timeout=settings.auth_service.timeout) as client:
                response = await client.post(
                    f"{settings.auth_service.url}/api/v1/users/batch/",
                    json={"user_ids": missing_ids}
                )

                if response.status_code == 200:
                    users_data = response.json()["users"]

                    # Сохраняем в кэш и результат
                    for user_id, user_data in users_data.items():
                        user_cache.set(user_id, user_data)
                        result[user_id] = user_data

        except Exception:
            # В случае ошибки возвращаем заглушки для недостающих пользователей
            for user_id in missing_ids:
                result[user_id] = {
                    "id": user_id,
                    "username": f"user_{user_id[:8]}",
                    "first_name": "Пользователь",
                    "last_name": user_id[:8],
                    "email": f"user_{user_id[:8]}@example.com"
                }

    return result


def format_user_name(user_data: Dict) -> str:
    """
    Форматирует имя пользователя для отображения в админке
    """
    if not user_data:
        return "Неизвестный пользователь"

    first_name = user_data.get("first_name", "")
    last_name = user_data.get("last_name", "")
    username = user_data.get("username", "")

    if first_name and last_name:
        return f"{first_name} {last_name} ({username})"
    elif username:
        return username
    else:
        return f"Пользователь {user_data.get('id', '')}"


def format_user_list(user_ids: List[str], users_data: Dict[str, Dict]) -> Dict[str, str]:
    """
    Форматирует список пользователей для отображения
    """
    result = {}
    for user_id in user_ids:
        user_data = users_data.get(user_id)
        result[user_id] = format_user_name(user_data)

    return result


class AdminPermissions:
    """Проверка прав доступа в админке"""

    @staticmethod
    def can_edit_course(user_data: Dict) -> bool:
        """Может ли пользователь редактировать курсы"""
        return user_data.get("is_superuser", False)

    @staticmethod
    def can_delete_user_data(user_data: Dict) -> bool:
        """Может ли пользователь удалять пользовательские данные"""
        return user_data.get("is_superuser", False)

    @staticmethod
    def can_view_all_submissions(user_data: Dict) -> bool:
        """Может ли пользователь видеть все отправки"""
        return user_data.get("is_superuser", False)


def safe_uuid_str(value) -> str:
    """Безопасное преобразование UUID в строку"""
    if not value:
        return ""

    if isinstance(value, uuid.UUID):
        return str(value)

    if isinstance(value, str):
        try:
            # Проверяем, что это валидный UUID
            uuid.UUID(value)
            return value
        except ValueError:
            return ""

    return str(value)


def truncate_text(text: str, max_length: int = 50) -> str:
    """Обрезает текст для отображения в таблице"""
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."
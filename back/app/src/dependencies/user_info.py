"""Зависимости для работы с пользователями из auth-сервиса"""

from typing import Dict, List, Optional
import uuid
from fastapi import Depends, HTTPException, status

from src.services.auth_service import auth_service, UserInfo


async def get_user_info(user_id: uuid.UUID) -> UserInfo:
    """
    Получить информацию о пользователе из auth-сервиса.
    Если пользователь не найден, возвращает 404 ошибку.
    """
    user_info = await auth_service.get_user_info(user_id)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    return user_info


async def verify_user_exists(user_id: uuid.UUID) -> uuid.UUID:
    """
    Проверить существование пользователя и вернуть его ID.
    Используется в эндпоинтах для валидации user_id.
    """
    exists = await auth_service.verify_user_exists(user_id)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    return user_id


async def get_users_info_batch(user_ids: List[uuid.UUID]) -> Dict[uuid.UUID, UserInfo]:
    """
    Получить информацию о нескольких пользователях одним запросом.
    Полезно для оптимизации при получении списков с информацией о пользователях.
    """
    return await auth_service.get_users_info(user_ids)


class UserInfoEnricher:
    """
    Класс для обогащения данных информацией о пользователях.
    Используется в сервисах для добавления пользовательской информации к моделям.
    """

    def __init__(self):
        self.auth_service = auth_service

    async def enrich_with_user_info(self, data: dict, user_id_field: str = "user_id") -> dict:
        """
        Обогатить данные информацией о пользователе.

        Args:
            data: Словарь с данными
            user_id_field: Название поля с ID пользователя

        Returns:
            Обогащенный словарь с информацией о пользователе в поле "user_info"
        """
        user_id = data.get(user_id_field)
        if user_id:
            user_info = await self.auth_service.get_user_info(user_id)
            if user_info:
                data["user_info"] = user_info.dict()
        return data

    async def enrich_list_with_users_info(
        self,
        items: List[dict],
        user_id_field: str = "user_id"
    ) -> List[dict]:
        """
        Обогатить список данных информацией о пользователях одним батч-запросом.

        Args:
            items: Список словарей с данными
            user_id_field: Название поля с ID пользователя

        Returns:
            Список обогащенных словарей
        """
        # Собираем уникальные user_id
        user_ids = set()
        for item in items:
            user_id = item.get(user_id_field)
            if user_id:
                user_ids.add(user_id)

        if not user_ids:
            return items

        # Получаем информацию о всех пользователях одним запросом
        users_info = await self.auth_service.get_users_info(list(user_ids))

        # Обогащаем каждый элемент
        for item in items:
            user_id = item.get(user_id_field)
            if user_id and user_id in users_info:
                item["user_info"] = users_info[user_id].dict()

        return items


# Синглтон для использования в сервисах
user_info_enricher = UserInfoEnricher()
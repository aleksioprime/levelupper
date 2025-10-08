""" Зависимости для проверки прав в группах """

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.core.schemas import UserJWT
from src.dependencies.group import get_group_service
from src.dependencies.permissions.base import permission_required
from src.services.group import GroupService


async def group_teacher_required(
    group_id: UUID,
    user: Annotated[UserJWT, Depends(permission_required())],
    group_service: Annotated[GroupService, Depends(get_group_service)],
) -> UserJWT:
    """
    Проверяет, что пользователь является преподавателем группы или админом
    """
    # Админы имеют полные права
    if user.is_admin or user.is_superuser:
        return user

    # TODO: Добавить проверку, является ли пользователь преподавателем группы
    # Пока что просто разрешаем всем авторизованным пользователям
    return user


async def group_member_required(
    group_id: UUID,
    user: Annotated[UserJWT, Depends(permission_required())],
    group_service: Annotated[GroupService, Depends(get_group_service)],
) -> UserJWT:
    """
    Проверяет, что пользователь является участником группы или админом
    """
    # Админы имеют полные права
    if user.is_admin or user.is_superuser:
        return user

    # TODO: Добавить проверку, является ли пользователь участником группы
    # Пока что просто разрешаем всем авторизованным пользователям
    return user
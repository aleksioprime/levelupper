"""Модуль с эндпоинтами для управления группами"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.core.schemas import UserJWT
from src.dependencies.group import get_group_service
from src.dependencies.security import permission_required
from src.schemas.group import GroupSchema, GroupCreateSchema, GroupUpdateSchema, GroupDetailSchema
from src.services.group import GroupService


router = APIRouter()

@router.get(
    path='/',
    summary='Получить все группы',
    response_model=list[GroupSchema],
    status_code=status.HTTP_200_OK,
)
async def get_groups(
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required())],
) -> list[GroupSchema]:
    """
    Возвращает список всех групп
    """
    groups = await service.get_all()
    return groups


@router.get(
    path='/{group_id}/',
    summary='Получить детальную информацию о группе',
    response_model=GroupDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_group(
        group_id: UUID,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required())],
) -> GroupDetailSchema:
    """
    Получает детальную информацию о группе
    """
    group = await service.get_detail_by_id(group_id)
    return group


@router.post(
    path='/',
    summary='Создаёт группу',
    status_code=status.HTTP_201_CREATED,
)
async def create_group(
        body: GroupCreateSchema,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> GroupSchema:
    """
    Создаёт новую группу
    """
    group = await service.create(body)
    return group


@router.patch(
    path='/{group_id}/',
    summary='Обновляет группу',
    response_model=GroupSchema,
    status_code=status.HTTP_200_OK,
)
async def update_group(
        group_id: UUID,
        body: GroupUpdateSchema,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> GroupSchema:
    """
    Обновляет группу по её ID
    """
    group = await service.update(group_id, body)
    return group


@router.delete(
    path='/{group_id}/',
    summary='Удаляет группу',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group(
        group_id: UUID,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> None:
    """
    Удаляет группу по её ID
    """
    await service.delete(group_id)
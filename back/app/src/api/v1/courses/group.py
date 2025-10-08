"""Модуль с эндпоинтами для управления группами"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.core.schemas import UserJWT
from src.dependencies.group import get_group_service
from src.dependencies.permissions.base import permission_required
from src.schemas.group import GroupSchema, GroupCreateSchema, GroupUpdateSchema, GroupDetailSchema
from src.schemas.enrollment import EnrollmentCreateSchema, EnrollmentUpdateSchema, EnrollmentListSchema, EnrollmentSchema
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


# Endpoints для управления участниками группы

@router.get(
    path='/{group_id}/enrollments/',
    summary='Получить список участников группы',
    response_model=EnrollmentListSchema,
    status_code=status.HTTP_200_OK,
)
async def get_group_enrollments(
        group_id: UUID,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required())],
) -> EnrollmentListSchema:
    """
    Получает список участников группы
    """
    return await service.get_group_enrollments(group_id)


@router.post(
    path='/{group_id}/enrollments/',
    summary='Добавить участника в группу',
    response_model=EnrollmentSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_group_enrollment(
        group_id: UUID,
        body: EnrollmentCreateSchema,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> EnrollmentSchema:
    """
    Добавляет участника в группу
    """
    return await service.add_enrollment(group_id, body)


@router.post(
    path='/{group_id}/students/{user_id}/',
    summary='Добавить студента в группу',
    response_model=EnrollmentSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_student_to_group(
        group_id: UUID,
        user_id: UUID,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> EnrollmentSchema:
    """
    Добавляет студента в группу
    """
    return await service.add_student(group_id, user_id)


@router.post(
    path='/{group_id}/teachers/{user_id}/',
    summary='Добавить преподавателя в группу',
    response_model=EnrollmentSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_teacher_to_group(
        group_id: UUID,
        user_id: UUID,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> EnrollmentSchema:
    """
    Добавляет преподавателя в группу
    """
    return await service.add_teacher(group_id, user_id)


@router.patch(
    path='/{group_id}/enrollments/{user_id}/',
    summary='Обновить данные участника группы',
    response_model=EnrollmentSchema,
    status_code=status.HTTP_200_OK,
)
async def update_group_enrollment(
        group_id: UUID,
        user_id: UUID,
        body: EnrollmentUpdateSchema,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> EnrollmentSchema:
    """
    Обновляет данные участника группы (роль, статус)
    """
    return await service.update_enrollment(group_id, user_id, body)


@router.delete(
    path='/{group_id}/enrollments/{user_id}/',
    summary='Удалить участника из группы',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_group_enrollment(
        group_id: UUID,
        user_id: UUID,
        service: Annotated[GroupService, Depends(get_group_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> None:
    """
    Удаляет участника из группы
    """
    await service.remove_enrollment(group_id, user_id)
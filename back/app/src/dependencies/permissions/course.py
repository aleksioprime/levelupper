""" Зависимости для проверки прав модераторов курса """

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.core.schemas import UserJWT
from src.dependencies.course import get_course_service
from src.dependencies.permissions.base import permission_required
from src.services.course import CourseService


async def course_moderator_required(
    course_id: UUID,
    user: Annotated[UserJWT, Depends(permission_required())],
    course_service: Annotated[CourseService, Depends(get_course_service)],
) -> UserJWT:
    """
    Проверяет, что пользователь является модератором курса или админом
    """
    # Админы имеют полные права
    if user.is_admin or user.is_superuser:
        return user

    # Проверяем, является ли пользователь модератором курса
    is_moderator = await course_service.is_course_moderator(course_id, user.id)
    if not is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется быть модератором курса или администратором."
        )

    return user


async def course_moderator_or_teacher_required(
    course_id: UUID,
    user: Annotated[UserJWT, Depends(permission_required())],
    course_service: Annotated[CourseService, Depends(get_course_service)],
) -> UserJWT:
    """
    Проверяет, что пользователь является модератором курса, преподавателем в группах курса или админом
    """
    # Админы имеют полные права
    if user.is_admin or user.is_superuser:
        return user

    # Проверяем, является ли пользователь модератором курса
    is_moderator = await course_service.is_course_moderator(course_id, user.id)
    if is_moderator:
        return user

    # TODO: Добавить проверку, является ли пользователь преподавателем в группах курса
    # Пока что просто запрещаем доступ, если не модератор и не админ
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав. Требуется быть модератором курса, преподавателем группы или администратором."
    )
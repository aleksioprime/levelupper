"""Модуль с эндпоинтами для управления курсами"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.core.schemas import UserJWT
from src.dependencies.course import get_course_service
from src.dependencies.security import permission_required
from src.schemas.course import CourseSchema, CourseCreateSchema, CourseUpdateSchema, CourseDetailSchema
from src.services.course import CourseService


router = APIRouter()

@router.get(
    path='/',
    summary='Получить все курсы',
    response_model=list[CourseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_courses(
        service: Annotated[CourseService, Depends(get_course_service)],
        user: Annotated[UserJWT, Depends(permission_required())],
) -> list[CourseSchema]:
    """
    Возвращает список всех курсов
    """
    courses = await service.get_all()
    return courses


@router.get(
    path='/{course_id}/',
    summary='Получить детальную информацию о курсе',
    response_model=CourseDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_course(
        course_id: UUID,
        service: Annotated[CourseService, Depends(get_course_service)],
        user: Annotated[UserJWT, Depends(permission_required())],
) -> CourseDetailSchema:
    """
    Получает детальную информацию о курсе
    """
    course = await service.get_detail_by_id(course_id)
    return course


@router.post(
    path='/',
    summary='Создаёт курс',
    status_code=status.HTTP_201_CREATED,
)
async def create_course(
        body: CourseCreateSchema,
        service: Annotated[CourseService, Depends(get_course_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> CourseSchema:
    """
    Создаёт новый курс
    """
    course = await service.create(body)
    return course


@router.patch(
    path='/{course_id}/',
    summary='Обновляет курс',
    response_model=CourseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_course(
        course_id: UUID,
        body: CourseUpdateSchema,
        service: Annotated[CourseService, Depends(get_course_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> CourseSchema:
    """
    Обновляет курс по его ID
    """
    course = await service.update(course_id, body)
    return course


@router.delete(
    path='/{course_id}/',
    summary='Удаляет курс',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_course(
        course_id: UUID,
        service: Annotated[CourseService, Depends(get_course_service)],
        user: Annotated[UserJWT, Depends(permission_required(admin=True))],
) -> None:
    """
    Удаляет курс по его ID
    """
    await service.delete(course_id)
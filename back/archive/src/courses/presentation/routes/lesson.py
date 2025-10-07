from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from src.courses.application.services import LessonService
from src.courses.application.schemas import (
    LessonCreateSchema, LessonUpdateSchema, LessonSchema
)
from src.courses.presentation.dependencies.lesson import get_lesson_service

router = APIRouter()


@router.post("/lessons/", response_model=LessonSchema, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    body: LessonCreateSchema,
    service: Annotated[LessonService, Depends(get_lesson_service)],
) -> LessonSchema:
    """Создание нового урока."""
    return await service.create(body)


@router.get("/lessons/{lesson_id}", response_model=LessonSchema)
async def get_lesson(
    lesson_id: UUID,
    service: Annotated[LessonService, Depends(get_lesson_service)],
) -> LessonSchema:
    """Получение урока по ID."""
    return await service.get_by_id(lesson_id)


@router.put("/lessons/{lesson_id}", response_model=LessonSchema)
async def update_lesson(
    lesson_id: UUID,
    body: LessonUpdateSchema,
    service: Annotated[LessonService, Depends(get_lesson_service)],
) -> LessonSchema:
    """Обновление урока."""
    return await service.update(lesson_id, body)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: UUID,
    service: Annotated[LessonService, Depends(get_lesson_service)],
):
    """Удаление урока."""
    deleted = await service.delete(lesson_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lesson not found")


@router.get("/courses/{course_id}/lessons", response_model=List[LessonSchema])
async def get_course_lessons(
    course_id: UUID,
    service: Annotated[LessonService, Depends(get_lesson_service)],
) -> List[LessonSchema]:
    """Получение всех уроков курса."""
    return await service.get_by_course_id(course_id)
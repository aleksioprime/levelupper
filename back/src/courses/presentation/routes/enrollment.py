from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from src.courses.application.services import EnrollmentService, LessonProgressService
from src.courses.application.schemas import (
    EnrollmentCreateSchema, EnrollmentSchema,
    LessonProgressSchema, LessonProgressUpdateSchema
)
from src.courses.presentation.dependencies.enrollment import get_enrollment_service, get_lesson_progress_service

router = APIRouter()


# === Enrollment endpoints ===
@router.post("/enrollments/", response_model=EnrollmentSchema, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    body: EnrollmentCreateSchema,
    service: Annotated[EnrollmentService, Depends(get_enrollment_service)],
) -> EnrollmentSchema:
    """Запись на курс."""
    return await service.enroll(body)


@router.get("/enrollments/{enrollment_id}", response_model=EnrollmentSchema)
async def get_enrollment(
    enrollment_id: UUID,
    service: Annotated[EnrollmentService, Depends(get_enrollment_service)],
) -> EnrollmentSchema:
    """Получение записи на курс по ID."""
    return await service.get_by_id(enrollment_id)


@router.get("/users/{user_id}/enrollments", response_model=List[EnrollmentSchema])
async def get_user_enrollments(
    user_id: UUID,
    service: Annotated[EnrollmentService, Depends(get_enrollment_service)],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[EnrollmentSchema]:
    """Получение всех записей пользователя на курсы."""
    return await service.get_by_user_id(user_id, limit, offset)


@router.get("/courses/{course_id}/enrollments", response_model=List[EnrollmentSchema])
async def get_course_enrollments(
    course_id: UUID,
    service: Annotated[EnrollmentService, Depends(get_enrollment_service)],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[EnrollmentSchema]:
    """Получение всех записей на курс."""
    return await service.get_by_course_id(course_id, limit, offset)


@router.put("/enrollments/{enrollment_id}/progress", response_model=EnrollmentSchema)
async def update_enrollment_progress(
    enrollment_id: UUID,
    service: Annotated[EnrollmentService, Depends(get_enrollment_service)],
    progress_percentage: float = Query(..., ge=0, le=100),
) -> EnrollmentSchema:
    """Обновление прогресса прохождения курса."""
    return await service.update_progress(enrollment_id, progress_percentage)


# === Lesson Progress endpoints ===
@router.post("/enrollments/{enrollment_id}/lessons/{lesson_id}/start", response_model=LessonProgressSchema)
async def start_lesson(
    enrollment_id: UUID,
    lesson_id: UUID,
    service: Annotated[LessonProgressService, Depends(get_lesson_progress_service)],
) -> LessonProgressSchema:
    """Начать урок."""
    return await service.start_lesson(enrollment_id, lesson_id)


@router.post("/enrollments/{enrollment_id}/lessons/{lesson_id}/complete", response_model=LessonProgressSchema)
async def complete_lesson(
    enrollment_id: UUID,
    lesson_id: UUID,
    service: Annotated[LessonProgressService, Depends(get_lesson_progress_service)],
) -> LessonProgressSchema:
    """Завершить урок."""
    return await service.complete_lesson(enrollment_id, lesson_id)


@router.put("/enrollments/{enrollment_id}/lessons/{lesson_id}/time", response_model=LessonProgressSchema)
async def update_lesson_time(
    enrollment_id: UUID,
    lesson_id: UUID,
    service: Annotated[LessonProgressService, Depends(get_lesson_progress_service)],
    additional_minutes: int = Query(..., ge=0),
) -> LessonProgressSchema:
    """Обновить время, потраченное на урок."""
    return await service.update_time_spent(enrollment_id, lesson_id, additional_minutes)


@router.get("/enrollments/{enrollment_id}/progress", response_model=List[LessonProgressSchema])
async def get_enrollment_progress(
    enrollment_id: UUID,
    service: Annotated[LessonProgressService, Depends(get_lesson_progress_service)],
) -> List[LessonProgressSchema]:
    """Получить прогресс по всем урокам курса."""
    return await service.get_by_enrollment_id(enrollment_id)
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from src.courses.application.services import AssignmentService, AssignmentSubmissionService
from src.courses.application.schemas import (
    AssignmentCreateSchema, AssignmentUpdateSchema, AssignmentSchema,
    AssignmentSubmissionCreateSchema, AssignmentSubmissionSchema,
    AssignmentSubmissionGradeSchema
)
from src.courses.presentation.dependencies.assignment import get_assignment_service, get_assignment_submission_service

router = APIRouter()


# === Assignment endpoints ===
@router.post("/assignments/", response_model=AssignmentSchema, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    body: AssignmentCreateSchema,
    service: Annotated[AssignmentService, Depends(get_assignment_service)],
) -> AssignmentSchema:
    """Создание нового задания."""
    return await service.create(body)


@router.get("/assignments/{assignment_id}", response_model=AssignmentSchema)
async def get_assignment(
    assignment_id: UUID,
    service: Annotated[AssignmentService, Depends(get_assignment_service)],
) -> AssignmentSchema:
    """Получение задания по ID."""
    return await service.get_by_id(assignment_id)


@router.put("/assignments/{assignment_id}", response_model=AssignmentSchema)
async def update_assignment(
    assignment_id: UUID,
    body: AssignmentUpdateSchema,
    service: Annotated[AssignmentService, Depends(get_assignment_service)],
) -> AssignmentSchema:
    """Обновление задания."""
    return await service.update(assignment_id, body)


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: UUID,
    service: Annotated[AssignmentService, Depends(get_assignment_service)],
):
    """Удаление задания."""
    deleted = await service.delete(assignment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Assignment not found")


@router.get("/lessons/{lesson_id}/assignments", response_model=List[AssignmentSchema])
async def get_lesson_assignments(
    lesson_id: UUID,
    service: Annotated[AssignmentService, Depends(get_assignment_service)],
) -> List[AssignmentSchema]:
    """Получение всех заданий урока."""
    return await service.get_by_lesson_id(lesson_id)


# === Assignment Submission endpoints ===
@router.post("/assignments/{assignment_id}/submissions", response_model=AssignmentSubmissionSchema, status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    assignment_id: UUID,
    body: AssignmentSubmissionCreateSchema,
    service: Annotated[AssignmentSubmissionService, Depends(get_assignment_submission_service)],
) -> AssignmentSubmissionSchema:
    """Отправка ответа на задание."""
    # Убеждаемся, что assignment_id совпадает
    body.assignment_id = assignment_id
    return await service.submit(body)


@router.get("/submissions/{submission_id}", response_model=AssignmentSubmissionSchema)
async def get_submission(
    submission_id: UUID,
    service: Annotated[AssignmentSubmissionService, Depends(get_assignment_submission_service)],
) -> AssignmentSubmissionSchema:
    """Получение ответа на задание по ID."""
    return await service.get_by_id(submission_id)


@router.put("/submissions/{submission_id}/grade", response_model=AssignmentSubmissionSchema)
async def grade_submission(
    submission_id: UUID,
    body: AssignmentSubmissionGradeSchema,
    service: Annotated[AssignmentSubmissionService, Depends(get_assignment_submission_service)],
) -> AssignmentSubmissionSchema:
    """Оценка ответа на задание."""
    return await service.grade(submission_id, body)


@router.get("/enrollments/{enrollment_id}/submissions", response_model=List[AssignmentSubmissionSchema])
async def get_enrollment_submissions(
    enrollment_id: UUID,
    service: Annotated[AssignmentSubmissionService, Depends(get_assignment_submission_service)],
) -> List[AssignmentSubmissionSchema]:
    """Получение всех ответов студента по курсу."""
    return await service.get_by_enrollment_id(enrollment_id)
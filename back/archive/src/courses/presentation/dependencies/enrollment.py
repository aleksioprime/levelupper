from typing import Annotated
from fastapi import Depends

from src.courses.infrastructure.sqlalchemy.uow import UnitOfWork
from src.courses.domain.uow import AbstractUnitOfWork
from src.courses.application.services import EnrollmentService, LessonProgressService


def get_unit_of_work() -> AbstractUnitOfWork:
    return UnitOfWork()


def get_enrollment_service(
    uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)],
) -> EnrollmentService:
    return EnrollmentService(uow)


def get_lesson_progress_service(
    uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)],
) -> LessonProgressService:
    return LessonProgressService(uow)
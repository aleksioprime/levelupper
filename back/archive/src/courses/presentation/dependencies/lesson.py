from typing import Annotated
from fastapi import Depends

from src.courses.infrastructure.sqlalchemy.uow import UnitOfWork
from src.courses.domain.uow import AbstractUnitOfWork
from src.courses.application.services import LessonService


def get_unit_of_work() -> AbstractUnitOfWork:
    return UnitOfWork()


def get_lesson_service(
    uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)],
) -> LessonService:
    return LessonService(uow)
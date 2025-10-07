from typing import Annotated
from fastapi import Depends

from src.courses.infrastructure.sqlalchemy.uow import UnitOfWork
from src.courses.domain.uow import AbstractUnitOfWork
from src.courses.application.services import CourseService


def get_unit_of_work() -> AbstractUnitOfWork:
    return UnitOfWork()


def get_course_service(
    uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)],
) -> CourseService:
    return CourseService(uow)

from typing import Annotated
from fastapi import Depends

from src.course.infrastructure.sqlalchemy.uow import UnitOfWork
from src.course.domain.uow import AbstractUnitOfWork
from src.course.application.services import CourseService


def get_unit_of_work() -> AbstractUnitOfWork:
    return UnitOfWork()


def get_course_service(
    uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)],
) -> CourseService:
    return CourseService(uow)

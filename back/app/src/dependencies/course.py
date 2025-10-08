""" Зависимость для получения экземпляра CourseService """

from typing import Annotated

from fastapi import Depends

from src.dependencies.uow import get_unit_of_work
from src.repositories.uow import UnitOfWork
from src.services.course import CourseService


async def get_course_service(
        uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
):
    return CourseService(uow=uow)
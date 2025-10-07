from typing import Annotated
from fastapi import Depends

from src.courses.infrastructure.sqlalchemy.uow import UnitOfWork
from src.courses.domain.uow import AbstractUnitOfWork
from src.courses.application.services import AssignmentService, AssignmentSubmissionService


def get_unit_of_work() -> AbstractUnitOfWork:
    return UnitOfWork()


def get_assignment_service(
    uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)],
) -> AssignmentService:
    return AssignmentService(uow)


def get_assignment_submission_service(
    uow: Annotated[AbstractUnitOfWork, Depends(get_unit_of_work)],
) -> AssignmentSubmissionService:
    return AssignmentSubmissionService(uow)
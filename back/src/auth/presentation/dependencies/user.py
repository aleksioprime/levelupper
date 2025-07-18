from typing import Annotated

from fastapi import Depends

from src.auth.presentation.dependencies.pagination import get_pagination_params
from src.auth.presentation.dependencies.uow import get_unit_of_work
from src.auth.application.services.user import UserService
from src.auth.application.schemas.pagination import BasePaginationParams
from src.auth.application.schemas.user import UserQueryParams
from src.auth.infrastructure.persistence.sqlalchemy.repositories.uow import UnitOfWork


def get_user_params(
        pagination: Annotated[BasePaginationParams, Depends(get_pagination_params)],
) -> UserQueryParams:
    """ Получает query-параметры фильтрации для пользователей """

    return UserQueryParams(
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def get_user_service(
        uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
):
    return UserService(uow)
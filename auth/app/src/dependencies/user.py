from typing import Annotated

from fastapi import Depends

from src.schemas.pagination import BasePaginationParams
from src.dependencies.pagination import get_pagination_params
from src.dependencies.uow import get_unit_of_work
from src.schemas.user import UserQueryParams
from src.repositories.uow import UnitOfWork
from src.services.user import UserService


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
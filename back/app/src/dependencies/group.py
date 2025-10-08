""" Зависимость для получения экземпляра GroupService """

from typing import Annotated

from fastapi import Depends

from src.dependencies.uow import get_unit_of_work
from src.repositories.uow import UnitOfWork
from src.services.group import GroupService


async def get_group_service(
        uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
):
    return GroupService(uow=uow)
""" Зависимость для получения экземпляра UnitOfWork """

from src.repositories.uow import UnitOfWork


async def get_unit_of_work():
    return UnitOfWork()
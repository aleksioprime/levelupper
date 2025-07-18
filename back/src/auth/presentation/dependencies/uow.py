from src.auth.infrastructure.persistence.sqlalchemy.repositories.uow import UnitOfWork
from src.auth.domain.uow import AbstractUnitOfWork


async def get_unit_of_work() -> AbstractUnitOfWork:
    return UnitOfWork()


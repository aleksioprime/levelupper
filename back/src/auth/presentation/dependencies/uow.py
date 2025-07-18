from src.auth.infrastructure.persistence.sqlalchemy.repositories.uow import UnitOfWork


async def get_unit_of_work():
    return UnitOfWork()
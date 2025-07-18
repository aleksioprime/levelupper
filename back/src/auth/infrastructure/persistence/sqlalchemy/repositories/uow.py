from src.common.db.postgres import async_session_maker

from src.auth.infrastructure.persistence.sqlalchemy.repositories.user import UserRepository
from src.auth.infrastructure.persistence.sqlalchemy.repositories.auth import AuthRepository
from src.auth.domain.uow import AbstractUnitOfWork


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()
        self.auth = AuthRepository(self.session)
        self.user = UserRepository(self.session)

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

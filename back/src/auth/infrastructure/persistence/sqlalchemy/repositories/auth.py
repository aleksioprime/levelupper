
from typing import List
from uuid import UUID

from sqlalchemy import select

from src.auth.infrastructure.persistence.sqlalchemy.models.user import User as ORMUser
from src.auth.infrastructure.persistence.sqlalchemy.repositories.base import BaseSQLRepository
from src.auth.domain.repositories.auth import BaseAuthRepository
from src.auth.infrastructure.persistence.sqlalchemy.mappers import orm_to_domain


class AuthRepository(BaseAuthRepository, BaseSQLRepository):

    async def get_user_by_username(self, username: str):
        """
        Получает пользователя по его имени
        """
        query = select(ORMUser).filter_by(username=username)
        result = await self.session.scalars(query)
        orm_user = result.one_or_none()
        return orm_to_domain(orm_user) if orm_user else None


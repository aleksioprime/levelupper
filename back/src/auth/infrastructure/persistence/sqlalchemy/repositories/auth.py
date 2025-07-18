
from typing import List
from uuid import UUID

from sqlalchemy import select

from src.auth.infrastructure.persistence.sqlalchemy.models.user import User
from src.auth.infrastructure.persistence.sqlalchemy.repositories.base import BaseSQLRepository
from src.auth.domain.repositories.auth import BaseAuthRepository


class AuthRepository(BaseAuthRepository, BaseSQLRepository):

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Получает пользователя по его имени
        """
        query = select(User).filter_by(username=username)
        result = await self.session.scalars(query)
        return result.one_or_none()

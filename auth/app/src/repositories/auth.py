from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from sqlalchemy import select

from src.models.user import User
from src.repositories.base import BaseSQLRepository


class BaseAuthRepository(ABC):
    ...


class AuthRepository(BaseAuthRepository, BaseSQLRepository):

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Получает пользователя по его имени
        """
        query = select(User).filter_by(username=username)
        result = await self.session.scalars(query)
        return result.one_or_none()

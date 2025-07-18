from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Tuple

from src.auth.domain.models.user import User
from src.auth.application.schemas.user import (
    UserUpdateSchema,
    UpdatePasswordUserSchema,
    UserQueryParams,
)


class BaseUserRepository(ABC):
    """Interface for user related persistence operations."""

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Return user by id or ``None`` if not found."""

    @abstractmethod
    async def get_user_all(self, params: UserQueryParams) -> Tuple[List[User], int]:
        """Return list of users and total count respecting pagination params."""

    @abstractmethod
    async def create(self, user: User) -> None:
        """Persist a new user instance."""

    @abstractmethod
    async def update(self, user_id: UUID, body: UserUpdateSchema) -> User:
        """Update user by id and return updated instance."""

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Remove user by id."""

    @abstractmethod
    async def update_password(self, user_id: UUID, body: UpdatePasswordUserSchema) -> None:
        """Update user password."""

    @abstractmethod
    async def update_photo(self, user_id: UUID, photo: str) -> None:
        """Update user's avatar url."""


from abc import ABC, abstractmethod
from uuid import UUID

from src.auth.domain.models.user import User


class BaseAuthRepository(ABC):
    """Interface for authentication related repository operations."""

    @abstractmethod
    async def get_user_by_username(self, username: str) -> User | None:
        """Return user by username or ``None`` if not found."""


from abc import ABC, abstractmethod

from src.auth.domain.repositories.auth import BaseAuthRepository
from src.auth.domain.repositories.user import BaseUserRepository


class AbstractUnitOfWork(ABC):
    auth: BaseAuthRepository
    user: BaseUserRepository

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...

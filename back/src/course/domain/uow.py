from abc import ABC, abstractmethod

from .repositories import AbstractCourseRepository


class AbstractUnitOfWork(ABC):
    courses: AbstractCourseRepository

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

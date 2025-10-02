from abc import ABC, abstractmethod
from uuid import UUID
from typing import List

from .models import Course


class AbstractCourseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, course_id: UUID) -> Course | None:
        ...

    @abstractmethod
    async def list(self, limit: int, offset: int) -> List[Course]:
        ...

    @abstractmethod
    async def create(self, course: Course) -> None:
        ...

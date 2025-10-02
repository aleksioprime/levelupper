from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class Course:
    """Domain entity representing a course."""

    id: UUID
    title: str
    description: str
    author_id: UUID

    @classmethod
    def create(cls, title: str, description: str, author_id: UUID) -> "Course":
        return cls(id=uuid4(), title=title, description=description, author_id=author_id)

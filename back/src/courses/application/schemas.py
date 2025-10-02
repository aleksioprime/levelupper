from uuid import UUID
from pydantic import BaseModel


class CourseCreateSchema(BaseModel):
    title: str
    description: str
    author_id: UUID


class CourseSchema(CourseCreateSchema):
    id: UUID

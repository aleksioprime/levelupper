import uuid
from uuid import UUID
from typing import List

from ..domain.models import Course
from ..domain.uow import AbstractUnitOfWork
from .schemas import CourseCreateSchema, CourseSchema
from src.common.exceptions.base import BaseException


class CourseService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create(self, body: CourseCreateSchema) -> CourseSchema:
        course = Course.create(
            title=body.title,
            description=body.description,
            author_id=body.author_id,
        )
        async with self.uow:
            await self.uow.courses.create(course)
        return CourseSchema(id=course.id, **body.dict())

    async def get_by_id(self, course_id: UUID) -> CourseSchema:
        async with self.uow:
            course = await self.uow.courses.get_by_id(course_id)
            if not course:
                raise BaseException(f"Course {course_id} not found")
        return CourseSchema(id=course.id, title=course.title, description=course.description, author_id=course.author_id)

    async def list(self, limit: int = 10, offset: int = 0) -> List[CourseSchema]:
        async with self.uow:
            courses = await self.uow.courses.list(limit, offset)
        return [CourseSchema(id=c.id, title=c.title, description=c.description, author_id=c.author_id) for c in courses]

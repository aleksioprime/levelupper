from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models import Course as DomainCourse
from ...domain.repositories import AbstractCourseRepository
from .models import Course as ORMCourse


class CourseRepository(AbstractCourseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, course_id: UUID) -> DomainCourse | None:
        orm = await self.session.get(ORMCourse, course_id)
        if orm is None:
            return None
        return DomainCourse(id=orm.id, title=orm.title, description=orm.description, author_id=orm.author_id)

    async def list(self, limit: int, offset: int) -> List[DomainCourse]:
        stmt = select(ORMCourse).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return [DomainCourse(id=row.id, title=row.title, description=row.description, author_id=row.author_id) for row in result.scalars().all()]

    async def create(self, course: DomainCourse) -> None:
        orm = ORMCourse(id=course.id, title=course.title, description=course.description, author_id=course.author_id)
        self.session.add(orm)
        await self.session.flush()

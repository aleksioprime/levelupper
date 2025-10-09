""" Репозиторий для работы с курсами """

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound

from src.models.course import Course, CourseTopic, CourseModerator
from src.schemas.course import CourseUpdateSchema


class CourseRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Course]:
        """ Получает список всех курсов """
        query = select(Course).order_by(Course.title.asc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_with_relations(self) -> list[Course]:
        """ Получает все курсы с связанными данными """
        query = (
            select(Course)
            .options(
                joinedload(Course.topics).joinedload(CourseTopic.lessons),
                joinedload(Course.groups),
                joinedload(Course.moderators)
            )
            .order_by(Course.title.asc())
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_by_id(self, course_id: UUID) -> Course:
        """ Получает курс по его ID """
        query = select(Course).where(Course.id == course_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_detail_by_id(self, course_id: UUID) -> Course:
        """ Получает детальную информацию о курсе по его ID """
        query = (
            select(Course)
            .options(
                joinedload(Course.topics).joinedload(CourseTopic.subtopics),
                joinedload(Course.topics).joinedload(CourseTopic.lessons),
                joinedload(Course.moderators)
            )
            .where(Course.id == course_id)
        )
        result = await self.session.execute(query)
        return result.unique().scalars().one_or_none()

    async def create(self, body: Course) -> None:
        """ Создаёт новый курс """
        create_data = body.model_dump(exclude_unset=True)
        course = Course(**create_data)
        self.session.add(course)
        await self.session.flush()
        return course

    async def update(self, course_id: UUID, body: CourseUpdateSchema) -> Course:
        """ Обновляет курс по его ID """
        update_data = {k: v for k, v in body.dict(exclude_unset=True).items()}
        if not update_data:
            raise NoResultFound("Нет данных для обновления")

        stmt = (
            update(Course)
            .where(Course.id == course_id)
            .values(**update_data)
        )
        await self.session.execute(stmt)
        return await self.get_by_id(course_id)

    async def delete(self, course_id: UUID) -> None:
        """ Удаляет курс по его ID """
        result = await self.get_by_id(course_id)
        if not result:
            raise NoResultFound(f"Курс с ID {course_id} не найден")

        await self.session.delete(result)

from uuid import UUID
from typing import List

from sqlalchemy.exc import IntegrityError, NoResultFound

from src.exceptions.base import BaseException
from src.repositories.uow import UnitOfWork
from src.schemas.course import CourseSchema, CourseUpdateSchema, CourseDetailSchema


class CourseService:
    """
    Сервис для управления курсами
    """
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all(self) -> List[CourseSchema]:
        """
        Выдаёт список всех курсов
        """
        async with self.uow:
            courses = await self.uow.course.get_all()

        return courses

    async def get_detail_by_id(self, course_id: UUID) -> CourseDetailSchema:
        """
        Выдаёт детальную информацию о курсе по его ID
        """
        async with self.uow:
            course = await self.uow.course.get_detail_by_id(course_id)
            if not course:
                raise BaseException(f"Курс с ID {course_id} не найден")
        return course

    async def create(self, body: CourseUpdateSchema) -> CourseSchema:
        """
        Создаёт новый курс
        """
        async with self.uow:
            try:
                created_course = await self.uow.course.create(body)
            except IntegrityError as exc:
                raise BaseException("Ошибка ограничения целостности данных в базе данных") from exc

        return created_course

    async def update(self, course_id: UUID, body: CourseUpdateSchema) -> CourseSchema:
        """
        Обновляет информацию о курсе по его ID
        """
        async with self.uow:
            try:
                updated_course = await self.uow.course.update(course_id, body)
            except NoResultFound as exc:
                raise BaseException(f"Курс с ID {course_id} не найден") from exc
        return updated_course

    async def delete(self, course_id: UUID) -> None:
        """
        Удаляет курс по его ID
        """
        async with self.uow:
            try:
                await self.uow.course.delete(course_id)
            except NoResultFound as exc:
                raise BaseException(f"Курс с ID {course_id} не найден") from exc
""" Репозиторий для работы с участниками групп """

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.exc import NoResultFound

from src.models.group import Enrollment
from src.constants.enrollment import EnrollmentRole, EnrollmentStatus


class EnrollmentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_enrollment(
        self,
        group_id: UUID,
        user_id: UUID,
        role: EnrollmentRole,
        status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    ) -> Enrollment:
        """ Добавляет участника в группу """
        enrollment = Enrollment(
            group_id=group_id,
            user_id=user_id,
            role=role,
            status=status
        )
        self.session.add(enrollment)
        await self.session.flush()
        return enrollment

    async def remove_enrollment(self, group_id: UUID, user_id: UUID) -> None:
        """ Удаляет участника из группы """
        stmt = delete(Enrollment).where(
            Enrollment.group_id == group_id,
            Enrollment.user_id == user_id
        )
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise NoResultFound(f"Участник {user_id} группы {group_id} не найден")

    async def update_enrollment_status(
        self,
        group_id: UUID,
        user_id: UUID,
        status: EnrollmentStatus
    ) -> Enrollment:
        """ Обновляет статус участника группы """
        stmt = (
            update(Enrollment)
            .where(
                Enrollment.group_id == group_id,
                Enrollment.user_id == user_id
            )
            .values(status=status)
        )
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise NoResultFound(f"Участник {user_id} группы {group_id} не найден")

        # Возвращаем обновленную запись
        query = select(Enrollment).where(
            Enrollment.group_id == group_id,
            Enrollment.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def update_enrollment_role(
        self,
        group_id: UUID,
        user_id: UUID,
        role: EnrollmentRole
    ) -> Enrollment:
        """ Обновляет роль участника группы """
        stmt = (
            update(Enrollment)
            .where(
                Enrollment.group_id == group_id,
                Enrollment.user_id == user_id
            )
            .values(role=role)
        )
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise NoResultFound(f"Участник {user_id} группы {group_id} не найден")

        # Возвращаем обновленную запись
        query = select(Enrollment).where(
            Enrollment.group_id == group_id,
            Enrollment.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_group_enrollments(self, group_id: UUID) -> list[Enrollment]:
        """ Получает список участников группы """
        query = select(Enrollment).where(Enrollment.group_id == group_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_enrollments(self, user_id: UUID) -> list[Enrollment]:
        """ Получает список групп пользователя """
        query = select(Enrollment).where(Enrollment.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_enrollment(self, group_id: UUID, user_id: UUID) -> Enrollment | None:
        """ Получает конкретную запись участника в группе """
        query = select(Enrollment).where(
            Enrollment.group_id == group_id,
            Enrollment.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def is_group_member(self, group_id: UUID, user_id: UUID) -> bool:
        """ Проверяет, является ли пользователь участником группы """
        enrollment = await self.get_enrollment(group_id, user_id)
        return enrollment is not None and enrollment.status == EnrollmentStatus.ACTIVE
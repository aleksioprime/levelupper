""" Репозиторий для работы с группами """

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound

from src.models.group import Group
from src.schemas.group import GroupUpdateSchema


class GroupRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Group]:
        """ Получает список всех групп """
        query = select(Group).order_by(Group.name.asc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, group_id: UUID) -> Group:
        """ Получает группу по её ID """
        query = select(Group).where(Group.id == group_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_detail_by_id(self, group_id: UUID) -> Group:
        """ Получает детальную информацию о группе по её ID """
        query = (
            select(Group)
            .options(
                joinedload(Group.enrollments)
            )
            .where(Group.id == group_id)
        )
        result = await self.session.execute(query)
        return result.unique().scalars().one_or_none()

    async def create(self, body: Group) -> None:
        """ Создаёт новую группу """
        create_data = body.model_dump(exclude_unset=True)
        group = Group(**create_data)
        self.session.add(group)
        await self.session.flush()
        return group

    async def update(self, group_id: UUID, body: GroupUpdateSchema) -> Group:
        """ Обновляет группу по её ID """
        update_data = {k: v for k, v in body.dict(exclude_unset=True).items()}
        if not update_data:
            raise NoResultFound("Нет данных для обновления")

        stmt = (
            update(Group)
            .where(Group.id == group_id)
            .values(**update_data)
        )
        await self.session.execute(stmt)
        return await self.get_by_id(group_id)

    async def delete(self, group_id: UUID) -> None:
        """ Удаляет группу по её ID """
        result = await self.get_by_id(group_id)
        if not result:
            raise NoResultFound(f"Группа с ID {group_id} не найдена")

        await self.session.delete(result)

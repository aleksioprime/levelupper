import argparse
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.auth.infrastructure.persistence.sqlalchemy.models.user import User
from src.common.db.postgres import async_session_maker

async def create_or_update_superuser(session: AsyncSession, username: str, password: str, email: str, force: bool):
    """
    Создаёт или обновляет суперпользователя.
    """
    default_first_name = "Администратор"
    default_last_name = "Администраторов"

    query = await session.execute(
        select(User).filter((User.username == username) | (User.email == email))
    )
    user = query.scalars().first()

    if user:
        if force:
            print(f"Обновляем данные суперпользователя {user.username}...")
            user.username = username
            user.password = password
            user.email = email
            user.is_superuser = True
            await session.commit()
            print(f"Суперпользователь {user.username} обновлён!")
        else:
            print(f"Суперпользователь {user.username} уже существует. Используйте --force для обновления.")
        return

    superuser = User(
        username=username,
        password=password,
        email=email,
        is_superuser=True,
        first_name=default_first_name,
        last_name=default_last_name,
    )
    session.add(superuser)
    try:
        await session.commit()
        print(f"Суперпользователь {username} успешно создан!")
    except IntegrityError as exc:
        await session.rollback()
        print(f"Ошибка при создании суперпользователя: {exc.orig}")

async def main():
    parser = argparse.ArgumentParser(description="Создание/обновление суперпользователя")
    parser.add_argument("--username", required=True, help="Логин суперпользователя")
    parser.add_argument("--password", required=True, help="Пароль суперпользователя")
    parser.add_argument("--email", required=True, help="E-mail суперпользователя")
    parser.add_argument("--force", action="store_true", help="Обновить данные, если суперпользователь уже существует")
    args = parser.parse_args()

    async with async_session_maker() as session:
        await create_or_update_superuser(session, args.username, args.password, args.email, args.force)

if __name__ == "__main__":
    asyncio.run(main())

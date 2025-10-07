from src.auth.domain.models.user import User
from src.auth.infrastructure.persistence.sqlalchemy.models.user import User as ORMUser


def orm_to_domain(user: ORMUser) -> User:
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        photo=user.photo,
        is_superuser=user.is_superuser,
        last_activity=user.last_activity,
        created_at=user.created_at,
    )


def domain_to_orm(user: User) -> ORMUser:
    orm_user = ORMUser(
        username=user.username,
        password=user.hashed_password,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_superuser=user.is_superuser,
    )
    orm_user.id = user.id
    orm_user.photo = user.photo
    orm_user.last_activity = user.last_activity
    orm_user.created_at = user.created_at
    return orm_user


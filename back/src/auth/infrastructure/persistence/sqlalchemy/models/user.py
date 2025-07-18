import uuid

from sqlalchemy import Column, DateTime, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from src.common.core.config import settings
from src.common.db.postgres import Base


class User(Base):
    """
    Модель пользователя. Содержит основную информацию о пользователе,
    а также связанные роли и организацию.
    """
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(255), unique=True, nullable=False)
    photo = Column(String(255), nullable=True)

    is_superuser = Column(Boolean, default=False, nullable=False)

    last_activity = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    def __init__(self, username: str,
                 password: str,
                 email: str,
                 first_name: str = "",
                 last_name: str = "",
                 is_superuser: bool = False,
                 ) -> None:
        self.username = username
        self.hashed_password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_superuser = is_superuser

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

    def __repr__(self) -> str:
        return f'<User {self.username}>'

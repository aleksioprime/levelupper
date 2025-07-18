from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class User:
    id: uuid.UUID
    username: str
    email: str
    hashed_password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    photo: Optional[str] = None
    is_superuser: bool = False
    last_activity: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def check_password(self, password: str) -> bool:
        # В domain-слое не должно быть зависимостей, поэтому просто заглушка.
        # Реальная проверка — через сервисы, внедряя hash_checker.
        raise NotImplementedError("check_password реализуется в сервисе приложения или через dependency injection")

    def __repr__(self) -> str:
        return f'<User {self.username}>'
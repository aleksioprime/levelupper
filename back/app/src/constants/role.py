from enum import StrEnum, auto


class RoleName(StrEnum):
    """Роли пользователей в системе"""
    ADMIN = auto()
    USER = auto()
    STUDENT = auto()
    TEACHER = auto()
    SUPERVISOR = auto()
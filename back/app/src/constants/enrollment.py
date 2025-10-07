from enum import StrEnum, auto


class EnrollmentRole(StrEnum):
    """Роль пользователя в группе"""
    STUDENT = auto()
    TEACHER = auto()
    SUPERVISOR = auto()
    ADMIN = auto()


class EnrollmentStatus(StrEnum):
    """Статус участия в курсе"""
    ACTIVE = auto()
    COMPLETED = auto()
    DROPPED = auto()
    PENDING = auto()
import enum


class EnrollmentStatus(enum.StrEnum):
    """Статус записи на курс"""
    enrolled = "enrolled"  # Записан
    in_progress = "in_progress"  # В процессе прохождения
    completed = "completed"  # Завершен
    dropped = "dropped"  # Отказался от прохождения
    suspended = "suspended"  # Приостановлен


class ProgressStatus(enum.StrEnum):
    """Статус прогресса по уроку"""
    not_started = "not_started"  # Не начат
    started = "started"  # Начат
    completed = "completed"  # Завершен
    skipped = "skipped"  # Пропущен
from enum import StrEnum, auto

class EventType(StrEnum):
    """Тип события"""
    LESSON = auto()          # Учебное занятие
    EXAM = auto()            # Экзамен или зачёт
    DEADLINE = auto()        # Дедлайн по заданию
    MEETING = auto()         # Собрание / встреча
    WEBINAR = auto()         # Онлайн мероприятие
    OTHER = auto()           # Другое
"""
Модели SQLAlchemy для приложения.

Этот модуль содержит все модели базы данных, используемые в приложении.
Включает модели для курсов, групп, заданий, вопросов и обратной связи.
Пользователи управляются отдельным auth-сервисом.
"""

# Базовые классы и миксины
from .base import Base, UUIDMixin, TimestampMixin

# Модель прогресса обучения
from .progress import Progress

# Модели курсов и структуры обучения
from .course import Course, CourseModerator, CourseTopic, Lesson

# Модели групп и записей
from .group import Group, Enrollment

# Модели заданий и отправок
from .assigment import Assignment, Submission, AnswerSubmission

# Модели вопросов и ответов
from .question import QuestionBlock, Question, AnswerOption

# Модели оценок и комментариев
from .feedback import Grade, Comment

# Экспорт всех моделей для удобного импорта
__all__ = [
    # Базовые классы
    "Base",
    "UUIDMixin",
    "TimestampMixin",

    # Прогресс обучения
    "Progress",

    # Курсы и обучение
    "Course",
    "CourseModerator",
    "CourseTopic",
    "Lesson",

    # Группы и записи
    "Group",
    "Enrollment",

    # Задания и отправки
    "Assignment",
    "Submission",
    "AnswerSubmission",

    # Вопросы и ответы
    "QuestionBlock",
    "Question",
    "AnswerOption",

    # Оценки и комментарии
    "Grade",
    "Comment",
]
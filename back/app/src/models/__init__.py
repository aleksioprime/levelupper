"""
Модели SQLAlchemy для приложения.

Этот модуль содержит все модели базы данных, используемые в приложении.
Включает модели для курсов, групп, пользователей, заданий, вопросов и обратной связи.
"""

# Базовые классы и миксины
from .base import Base, UUIDMixin, TimestampMixin

# Модели пользователей и прогресса
from .user import User, Progress

# Модели курсов и структуры обучения
from .course import Course, CourseTopic, Lesson

# Модели групп и записей
from .groups import Group, Enrollment

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

    # Пользователи и прогресс
    "User",
    "Progress",

    # Курсы и обучение
    "Course",
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
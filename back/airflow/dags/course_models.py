"""
Модели курсов для Airflow DAG'ов
Совместимость с SQLAlchemy 1.4.x
"""
import uuid
from datetime import date

from sqlalchemy import Column, Text, String, ForeignKey, Integer, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models_base import Base, UUIDMixin, TimestampMixin


class Course(UUIDMixin, TimestampMixin, Base):
    """
    Модель курса.
    Содержит основную информацию о курсе и связь с группами
    """
    __tablename__ = "courses"

    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"Курс {self.title}"


class CourseModerator(UUIDMixin, TimestampMixin, Base):
    """
    Модель модератора курса.
    Связывает курс с пользователем из auth сервиса
    """
    __tablename__ = "course_moderators"
    __table_args__ = (
        UniqueConstraint('course_id', 'user_id', name='uq_course_moderator'),
    )

    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ID пользователя из auth сервиса
    user_id = Column(UUID(as_uuid=True), nullable=False)

    def __repr__(self) -> str:
        return f"Модератор {self.user_id} курса {self.course_id}"


class CourseTopic(UUIDMixin, TimestampMixin, Base):
    """
    Модель темы курса.
    Тема может быть частью курса или подтемой другой темы.
    """
    __tablename__ = "course_topics"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)

    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("course_topics.id", ondelete="CASCADE"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"Тема курса: {self.title}"


class Lesson(UUIDMixin, TimestampMixin, Base):
    """
    Модель урока.
    Хранит основную информацию о конкретном занятии.
    """
    __tablename__ = "lessons"

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    date = Column(Date, nullable=True)

    topic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("course_topics.id", ondelete="CASCADE"),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"Урок: {self.title}"


__all__ = ["Course", "CourseModerator", "CourseTopic", "Lesson"]
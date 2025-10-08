"""Модели курса, тем курса и уроков"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Text, String, ForeignKey, Integer, Date, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class Course(UUIDMixin, TimestampMixin, Base):
    """
    Модель курса.
    Содержит основную информацию о курсе и связь с группами
    """
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    groups: Mapped[list["Group"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )

    topics: Mapped[list["CourseTopic"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )

    moderators: Mapped[list["CourseModerator"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )

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

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    course: Mapped["Course"] = relationship(back_populates="moderators")

    # ID пользователя из auth сервиса
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)

    def __repr__(self) -> str:
        return f"Модератор {self.user_id} курса {self.course.title}"


class CourseTopic(UUIDMixin, TimestampMixin, Base):
    """
    Модель темы курса.
    Тема может быть частью курса или подтемой другой темы.
    """
    __tablename__ = "course_topics"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    course: Mapped["Course"] = relationship(back_populates="topics")

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("course_topics.id", ondelete="CASCADE"),
        nullable=True,
    )
    parent: Mapped["CourseTopic"] = relationship(
        back_populates="subtopics",
        remote_side="CourseTopic.id",
    )

    subtopics: Mapped[list["CourseTopic"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Тема курса: {self.title}"


class Lesson(UUIDMixin, TimestampMixin, Base):
    """
    Модель урока.
    Хранит основную информацию о конкретном занятии.
    """
    __tablename__ = "lessons"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    date: Mapped[date | None] = mapped_column(Date)

    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_topics.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic: Mapped["CourseTopic"] = relationship(back_populates="lessons")

    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Урок: {self.title}"


__all__ = ["Course", "CourseModerator", "CourseTopic", "Lesson"]
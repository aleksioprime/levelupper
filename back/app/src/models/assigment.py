
"""Модели заданий, отправок и ответов студентов"""

from datetime import datetime, date
from sqlalchemy import String, Text, Boolean, Date, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base, UUIDMixin, TimestampMixin
from src.constants.assigment import AssignmentType


class Assignment(UUIDMixin, TimestampMixin, Base):
    """
    Модель задания.
    Задание может принадлежать как уроку, так и теме.
    """
    __tablename__ = "assignments"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[AssignmentType] = mapped_column(Enum(AssignmentType), default=AssignmentType.PRACTICE)

    due_date: Mapped[date | None] = mapped_column(Date)

    max_score: Mapped[int | None] = mapped_column(Integer, default=100)
    max_attempts: Mapped[int | None] = mapped_column(Integer, default=1)
    allow_retry_after_success: Mapped[bool] = mapped_column(Boolean, default=False)

    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("course_topics.id", ondelete="CASCADE"),
        nullable=True,
    )
    topic: Mapped["CourseTopic" | None] = relationship(back_populates="assignments")

    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=True,
    )
    lesson: Mapped["Lesson" | None] = relationship(back_populates="assignments")

    question_blocks: Mapped[list["QuestionBlock"]] = relationship(
        back_populates="assignment",
        cascade="all, delete-orphan",
    )

    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="assignment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Задание: {self.title}"


class Submission(UUIDMixin, TimestampMixin, Base):
    """
    Отправка студентом работы или теста.
    """
    __tablename__ = "submissions"

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    score: Mapped[int | None] = mapped_column(Integer)
    submitted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"))
    assignment: Mapped["Assignment"] = relationship(back_populates="submissions")

    answers: Mapped[list["AnswerSubmission"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
    )

    grade: Mapped["Grade" | None] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        uselist=False,
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
    )


class AnswerSubmission(UUIDMixin, Base):
    """
    Ответ студента на отдельный вопрос.
    Может хранить выбранный вариант или текстовый ответ.
    """
    __tablename__ = "answer_submissions"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assignment_questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    answer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("answer_options.id", ondelete="SET NULL"),
    )

    text_answer: Mapped[str | None] = mapped_column(Text)
    is_correct: Mapped[bool | None] = mapped_column(Boolean)

    submission: Mapped["Submission"] = relationship(back_populates="answers")


__all__ = ["Assignment", "Submission", "AnswerSubmission"]

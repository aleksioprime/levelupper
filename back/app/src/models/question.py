"""Модели вопросов, блоков вопросов и вариантов ответов"""

import uuid

from sqlalchemy import Text, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class QuestionBlock(UUIDMixin, TimestampMixin, Base):
    """
    Блок вопросов — часть задания, объединяющая группу вопросов.
    """
    __tablename__ = "question_blocks"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
    )
    assignment: Mapped["Assignment"] = relationship(back_populates="question_blocks")

    questions: Mapped[list["Question"]] = relationship(
        back_populates="block",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"Блок вопросов: {self.title}"


class Question(UUIDMixin, TimestampMixin, Base):
    """
    Вопрос внутри блока
    """
    __tablename__ = "assignment_questions"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    multiple: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    block_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("question_blocks.id", ondelete="CASCADE"),
        nullable=False,
    )
    block: Mapped["QuestionBlock"] = relationship(back_populates="questions")

    options: Mapped[list["AnswerOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )


class AnswerOption(UUIDMixin, Base):
    """
    Вариант ответа на вопрос.
    """
    __tablename__ = "answer_options"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question: Mapped["Question"] = relationship(back_populates="options")


__all__ = ["QuestionBlock", "Question", "AnswerOption"]

from sqlalchemy import ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid

from .base import Base, UUIDMixin, TimestampMixin


class Grade(UUIDMixin, TimestampMixin, Base):
    """
    Оценка за задание.
    Преподаватель выставляет балл и, при необходимости, комментарий
    """
    __tablename__ = "grades"

    value: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    submission: Mapped["Submission"] = relationship(back_populates="grade")
    teacher: Mapped["User" | None] = relationship()

    graded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Оценка {self.value} (submission={self.submission_id})"



class Comment(UUIDMixin, TimestampMixin, Base):
    """
    Комментарий преподавателя.
    Может быть к попытке студента или конкретному вопросу
    """
    __tablename__ = "comments"

    text: Mapped[str] = mapped_column(Text, nullable=False)

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    teacher: Mapped["User" | None] = relationship()

    submission_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
    )
    submission: Mapped["Submission" | None] = relationship(back_populates="comments")

    question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
    )
    question: Mapped["Question" | None] = relationship(back_populates="comments")

    def __repr__(self):
        return f"Комментарий от {self.teacher_id}: {self.text[:40]}"

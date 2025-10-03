import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime,
    ForeignKey, DECIMAL, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.common.db.postgres import Base


class Course(Base):
    """SQLAlchemy модель курса."""
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    level = Column(String(50), nullable=False, default="beginner")
    status = Column(String(50), nullable=False, default="draft")
    price = Column(DECIMAL(10, 2), nullable=True)
    duration_hours = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    tags = Column(ARRAY(String), nullable=False, default=[])
    image_url = Column(String(500), nullable=True)
    is_free = Column(Boolean, nullable=False, default=True)
    max_students = Column(Integer, nullable=True)

    # Отношения
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    """SQLAlchemy модель урока."""
    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    lesson_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    order_index = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    video_url = Column(String(500), nullable=True)
    materials = Column(JSONB, nullable=False, default=[])
    is_free_preview = Column(Boolean, nullable=False, default=False)

    # Отношения
    course = relationship("Course", back_populates="lessons")
    assignments = relationship("Assignment", back_populates="lesson", cascade="all, delete-orphan")
    progress_records = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")


class Assignment(Base):
    """SQLAlchemy модель задания."""
    __tablename__ = "assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    assignment_type = Column(String(50), nullable=False)
    questions = Column(JSONB, nullable=False, default=[])
    max_score = Column(Integer, nullable=False, default=100)
    passing_score = Column(Integer, nullable=False, default=60)
    time_limit_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_required = Column(Boolean, nullable=False, default=True)

    # Отношения
    lesson = relationship("Lesson", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class Enrollment(Base):
    """SQLAlchemy модель записи на курс."""
    __tablename__ = "enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    status = Column(String(50), nullable=False, default="enrolled")
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    progress_percentage = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    certificate_issued = Column(Boolean, nullable=False, default=False)

    # Отношения
    course = relationship("Course", back_populates="enrollments")
    lesson_progress = relationship("LessonProgress", back_populates="enrollment", cascade="all, delete-orphan")
    submissions = relationship("AssignmentSubmission", back_populates="enrollment", cascade="all, delete-orphan")


class LessonProgress(Base):
    """SQLAlchemy модель прогресса по уроку."""
    __tablename__ = "lesson_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("enrollments.id"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    status = Column(String(50), nullable=False, default="not_started")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_minutes = Column(Integer, nullable=False, default=0)

    # Отношения
    enrollment = relationship("Enrollment", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress_records")


class AssignmentSubmission(Base):
    """SQLAlchemy модель ответа на задание."""
    __tablename__ = "assignment_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("enrollments.id"), nullable=False)
    answers = Column(JSONB, nullable=False, default={})
    score = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="submitted")
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    graded_at = Column(DateTime(timezone=True), nullable=True)
    feedback = Column(Text, nullable=True)
    attempt_number = Column(Integer, nullable=False, default=1)

    # Отношения
    assignment = relationship("Assignment", back_populates="submissions")
    enrollment = relationship("Enrollment", back_populates="submissions")

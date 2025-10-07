from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.models import (
    Course as DomainCourse,
    Lesson as DomainLesson,
    Assignment as DomainAssignment,
    Enrollment as DomainEnrollment,
    LessonProgress as DomainLessonProgress,
    AssignmentSubmission as DomainAssignmentSubmission
)
from ...domain.repositories import (
    AbstractCourseRepository,
    AbstractLessonRepository,
    AbstractAssignmentRepository,
    AbstractEnrollmentRepository,
    AbstractLessonProgressRepository,
    AbstractAssignmentSubmissionRepository
)
from .models import (
    Course as ORMCourse,
    Lesson as ORMLesson,
    Assignment as ORMAssignment,
    Enrollment as ORMEnrollment,
    LessonProgress as ORMLessonProgress,
    AssignmentSubmission as ORMAssignmentSubmission
)


class CourseRepository(AbstractCourseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _orm_to_domain(self, orm: ORMCourse) -> DomainCourse:
        """Преобразование ORM модели в доменную."""
        return DomainCourse(
            id=orm.id,
            title=orm.title,
            description=orm.description,
            author_id=orm.author_id,
            level=orm.level,
            status=orm.status,
            price=orm.price,
            duration_hours=orm.duration_hours,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            tags=orm.tags or [],
            image_url=orm.image_url,
            is_free=orm.is_free,
            max_students=orm.max_students
        )

    def _domain_to_orm(self, domain: DomainCourse) -> ORMCourse:
        """Преобразование доменной модели в ORM."""
        return ORMCourse(
            id=domain.id,
            title=domain.title,
            description=domain.description,
            author_id=domain.author_id,
            level=domain.level,
            status=domain.status,
            price=domain.price,
            duration_hours=domain.duration_hours,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            tags=domain.tags,
            image_url=domain.image_url,
            is_free=domain.is_free,
            max_students=domain.max_students
        )

    async def get_by_id(self, course_id: UUID) -> Optional[DomainCourse]:
        orm = await self.session.get(ORMCourse, course_id)
        return self._orm_to_domain(orm) if orm else None

    async def list(self, limit: int, offset: int) -> List[DomainCourse]:
        stmt = select(ORMCourse).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]

    async def create(self, course: DomainCourse) -> None:
        orm = self._domain_to_orm(course)
        self.session.add(orm)
        await self.session.flush()

    async def update(self, course: DomainCourse) -> None:
        stmt = (
            update(ORMCourse)
            .where(ORMCourse.id == course.id)
            .values(
                title=course.title,
                description=course.description,
                level=course.level,
                status=course.status,
                price=course.price,
                duration_hours=course.duration_hours,
                updated_at=course.updated_at,
                tags=course.tags,
                image_url=course.image_url,
                is_free=course.is_free,
                max_students=course.max_students
            )
        )
        await self.session.execute(stmt)

    async def delete(self, course_id: UUID) -> bool:
        stmt = delete(ORMCourse).where(ORMCourse.id == course_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_by_author(self, author_id: UUID, limit: int, offset: int) -> List[DomainCourse]:
        stmt = (
            select(ORMCourse)
            .where(ORMCourse.author_id == author_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]


class LessonRepository(AbstractLessonRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _orm_to_domain(self, orm: ORMLesson) -> DomainLesson:
        return DomainLesson(
            id=orm.id,
            course_id=orm.course_id,
            title=orm.title,
            content=orm.content,
            lesson_type=orm.lesson_type,
            status=orm.status,
            order_index=orm.order_index,
            duration_minutes=orm.duration_minutes,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            video_url=orm.video_url,
            materials=orm.materials or [],
            is_free_preview=orm.is_free_preview
        )

    def _domain_to_orm(self, domain: DomainLesson) -> ORMLesson:
        return ORMLesson(
            id=domain.id,
            course_id=domain.course_id,
            title=domain.title,
            content=domain.content,
            lesson_type=domain.lesson_type,
            status=domain.status,
            order_index=domain.order_index,
            duration_minutes=domain.duration_minutes,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            video_url=domain.video_url,
            materials=domain.materials,
            is_free_preview=domain.is_free_preview
        )

    async def get_by_id(self, lesson_id: UUID) -> Optional[DomainLesson]:
        orm = await self.session.get(ORMLesson, lesson_id)
        return self._orm_to_domain(orm) if orm else None

    async def get_by_course_id(self, course_id: UUID) -> List[DomainLesson]:
        stmt = (
            select(ORMLesson)
            .where(ORMLesson.course_id == course_id)
            .order_by(ORMLesson.order_index)
        )
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]

    async def create(self, lesson: DomainLesson) -> None:
        orm = self._domain_to_orm(lesson)
        self.session.add(orm)
        await self.session.flush()

    async def update(self, lesson: DomainLesson) -> None:
        stmt = (
            update(ORMLesson)
            .where(ORMLesson.id == lesson.id)
            .values(
                title=lesson.title,
                content=lesson.content,
                lesson_type=lesson.lesson_type,
                status=lesson.status,
                order_index=lesson.order_index,
                duration_minutes=lesson.duration_minutes,
                updated_at=lesson.updated_at,
                video_url=lesson.video_url,
                materials=lesson.materials,
                is_free_preview=lesson.is_free_preview
            )
        )
        await self.session.execute(stmt)

    async def delete(self, lesson_id: UUID) -> bool:
        stmt = delete(ORMLesson).where(ORMLesson.id == lesson_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class AssignmentRepository(AbstractAssignmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _orm_to_domain(self, orm: ORMAssignment) -> DomainAssignment:
        return DomainAssignment(
            id=orm.id,
            lesson_id=orm.lesson_id,
            title=orm.title,
            description=orm.description,
            assignment_type=orm.assignment_type,
            questions=orm.questions or [],
            max_score=orm.max_score,
            passing_score=orm.passing_score,
            time_limit_minutes=orm.time_limit_minutes,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            is_required=orm.is_required
        )

    def _domain_to_orm(self, domain: DomainAssignment) -> ORMAssignment:
        return ORMAssignment(
            id=domain.id,
            lesson_id=domain.lesson_id,
            title=domain.title,
            description=domain.description,
            assignment_type=domain.assignment_type,
            questions=domain.questions,
            max_score=domain.max_score,
            passing_score=domain.passing_score,
            time_limit_minutes=domain.time_limit_minutes,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            is_required=domain.is_required
        )

    async def get_by_id(self, assignment_id: UUID) -> Optional[DomainAssignment]:
        orm = await self.session.get(ORMAssignment, assignment_id)
        return self._orm_to_domain(orm) if orm else None

    async def get_by_lesson_id(self, lesson_id: UUID) -> List[DomainAssignment]:
        stmt = select(ORMAssignment).where(ORMAssignment.lesson_id == lesson_id)
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]

    async def create(self, assignment: DomainAssignment) -> None:
        orm = self._domain_to_orm(assignment)
        self.session.add(orm)
        await self.session.flush()

    async def update(self, assignment: DomainAssignment) -> None:
        stmt = (
            update(ORMAssignment)
            .where(ORMAssignment.id == assignment.id)
            .values(
                title=assignment.title,
                description=assignment.description,
                assignment_type=assignment.assignment_type,
                questions=assignment.questions,
                max_score=assignment.max_score,
                passing_score=assignment.passing_score,
                time_limit_minutes=assignment.time_limit_minutes,
                updated_at=assignment.updated_at,
                is_required=assignment.is_required
            )
        )
        await self.session.execute(stmt)

    async def delete(self, assignment_id: UUID) -> bool:
        stmt = delete(ORMAssignment).where(ORMAssignment.id == assignment_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class EnrollmentRepository(AbstractEnrollmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _orm_to_domain(self, orm: ORMEnrollment) -> DomainEnrollment:
        return DomainEnrollment(
            id=orm.id,
            user_id=orm.user_id,
            course_id=orm.course_id,
            status=orm.status,
            enrolled_at=orm.enrolled_at,
            completed_at=orm.completed_at,
            progress_percentage=float(orm.progress_percentage),
            last_accessed_at=orm.last_accessed_at,
            certificate_issued=orm.certificate_issued
        )

    def _domain_to_orm(self, domain: DomainEnrollment) -> ORMEnrollment:
        return ORMEnrollment(
            id=domain.id,
            user_id=domain.user_id,
            course_id=domain.course_id,
            status=domain.status,
            enrolled_at=domain.enrolled_at,
            completed_at=domain.completed_at,
            progress_percentage=domain.progress_percentage,
            last_accessed_at=domain.last_accessed_at,
            certificate_issued=domain.certificate_issued
        )

    async def get_by_id(self, enrollment_id: UUID) -> Optional[DomainEnrollment]:
        orm = await self.session.get(ORMEnrollment, enrollment_id)
        return self._orm_to_domain(orm) if orm else None

    async def get_by_user_and_course(self, user_id: UUID, course_id: UUID) -> Optional[DomainEnrollment]:
        stmt = select(ORMEnrollment).where(
            and_(ORMEnrollment.user_id == user_id, ORMEnrollment.course_id == course_id)
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._orm_to_domain(orm) if orm else None

    async def get_by_user_id(self, user_id: UUID, limit: int, offset: int) -> List[DomainEnrollment]:
        stmt = (
            select(ORMEnrollment)
            .where(ORMEnrollment.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]

    async def get_by_course_id(self, course_id: UUID, limit: int, offset: int) -> List[DomainEnrollment]:
        stmt = (
            select(ORMEnrollment)
            .where(ORMEnrollment.course_id == course_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]

    async def create(self, enrollment: DomainEnrollment) -> None:
        orm = self._domain_to_orm(enrollment)
        self.session.add(orm)
        await self.session.flush()

    async def update(self, enrollment: DomainEnrollment) -> None:
        stmt = (
            update(ORMEnrollment)
            .where(ORMEnrollment.id == enrollment.id)
            .values(
                status=enrollment.status,
                completed_at=enrollment.completed_at,
                progress_percentage=enrollment.progress_percentage,
                last_accessed_at=enrollment.last_accessed_at,
                certificate_issued=enrollment.certificate_issued
            )
        )
        await self.session.execute(stmt)

    async def delete(self, enrollment_id: UUID) -> bool:
        stmt = delete(ORMEnrollment).where(ORMEnrollment.id == enrollment_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class LessonProgressRepository(AbstractLessonProgressRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _orm_to_domain(self, orm: ORMLessonProgress) -> DomainLessonProgress:
        return DomainLessonProgress(
            id=orm.id,
            enrollment_id=orm.enrollment_id,
            lesson_id=orm.lesson_id,
            status=orm.status,
            started_at=orm.started_at,
            completed_at=orm.completed_at,
            time_spent_minutes=orm.time_spent_minutes
        )

    def _domain_to_orm(self, domain: DomainLessonProgress) -> ORMLessonProgress:
        return ORMLessonProgress(
            id=domain.id,
            enrollment_id=domain.enrollment_id,
            lesson_id=domain.lesson_id,
            status=domain.status,
            started_at=domain.started_at,
            completed_at=domain.completed_at,
            time_spent_minutes=domain.time_spent_minutes
        )

    async def get_by_id(self, progress_id: UUID) -> Optional[DomainLessonProgress]:
        orm = await self.session.get(ORMLessonProgress, progress_id)
        return self._orm_to_domain(orm) if orm else None

    async def get_by_enrollment_and_lesson(self, enrollment_id: UUID, lesson_id: UUID) -> Optional[DomainLessonProgress]:
        stmt = select(ORMLessonProgress).where(
            and_(ORMLessonProgress.enrollment_id == enrollment_id, ORMLessonProgress.lesson_id == lesson_id)
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._orm_to_domain(orm) if orm else None

    async def get_by_enrollment_id(self, enrollment_id: UUID) -> List[DomainLessonProgress]:
        stmt = select(ORMLessonProgress).where(ORMLessonProgress.enrollment_id == enrollment_id)
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]

    async def create(self, progress: DomainLessonProgress) -> None:
        orm = self._domain_to_orm(progress)
        self.session.add(orm)
        await self.session.flush()

    async def update(self, progress: DomainLessonProgress) -> None:
        stmt = (
            update(ORMLessonProgress)
            .where(ORMLessonProgress.id == progress.id)
            .values(
                status=progress.status,
                started_at=progress.started_at,
                completed_at=progress.completed_at,
                time_spent_minutes=progress.time_spent_minutes
            )
        )
        await self.session.execute(stmt)


class AssignmentSubmissionRepository(AbstractAssignmentSubmissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _orm_to_domain(self, orm: ORMAssignmentSubmission) -> DomainAssignmentSubmission:
        return DomainAssignmentSubmission(
            id=orm.id,
            assignment_id=orm.assignment_id,
            enrollment_id=orm.enrollment_id,
            answers=orm.answers or {},
            score=orm.score,
            status=orm.status,
            submitted_at=orm.submitted_at,
            graded_at=orm.graded_at,
            feedback=orm.feedback,
            attempt_number=orm.attempt_number
        )

    def _domain_to_orm(self, domain: DomainAssignmentSubmission) -> ORMAssignmentSubmission:
        return ORMAssignmentSubmission(
            id=domain.id,
            assignment_id=domain.assignment_id,
            enrollment_id=domain.enrollment_id,
            answers=domain.answers,
            score=domain.score,
            status=domain.status,
            submitted_at=domain.submitted_at,
            graded_at=domain.graded_at,
            feedback=domain.feedback,
            attempt_number=domain.attempt_number
        )

    async def get_by_id(self, submission_id: UUID) -> Optional[DomainAssignmentSubmission]:
        orm = await self.session.get(ORMAssignmentSubmission, submission_id)
        return self._orm_to_domain(orm) if orm else None

    async def get_by_assignment_and_enrollment(self, assignment_id: UUID, enrollment_id: UUID) -> List[DomainAssignmentSubmission]:
        stmt = (
            select(ORMAssignmentSubmission)
            .where(
                and_(
                    ORMAssignmentSubmission.assignment_id == assignment_id,
                    ORMAssignmentSubmission.enrollment_id == enrollment_id
                )
            )
            .order_by(ORMAssignmentSubmission.attempt_number.desc())
        )
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]

    async def get_by_enrollment_id(self, enrollment_id: UUID) -> List[DomainAssignmentSubmission]:
        stmt = select(ORMAssignmentSubmission).where(ORMAssignmentSubmission.enrollment_id == enrollment_id)
        result = await self.session.execute(stmt)
        return [self._orm_to_domain(row) for row in result.scalars().all()]

    async def create(self, submission: DomainAssignmentSubmission) -> None:
        orm = self._domain_to_orm(submission)
        self.session.add(orm)
        await self.session.flush()

    async def update(self, submission: DomainAssignmentSubmission) -> None:
        stmt = (
            update(ORMAssignmentSubmission)
            .where(ORMAssignmentSubmission.id == submission.id)
            .values(
                answers=submission.answers,
                score=submission.score,
                status=submission.status,
                submitted_at=submission.submitted_at,
                graded_at=submission.graded_at,
                feedback=submission.feedback
            )
        )
        await self.session.execute(stmt)

    async def get_latest_by_assignment_and_enrollment(self, assignment_id: UUID, enrollment_id: UUID) -> Optional[DomainAssignmentSubmission]:
        stmt = (
            select(ORMAssignmentSubmission)
            .where(
                and_(
                    ORMAssignmentSubmission.assignment_id == assignment_id,
                    ORMAssignmentSubmission.enrollment_id == enrollment_id
                )
            )
            .order_by(ORMAssignmentSubmission.attempt_number.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._orm_to_domain(orm) if orm else None

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import List, Optional, Dict, Any

from ..domain.models import (
    Course, Lesson, Assignment, Enrollment,
    LessonProgress, AssignmentSubmission
)
from ..domain.uow import AbstractUnitOfWork
from .schemas import (
    CourseCreateSchema, CourseUpdateSchema, CourseSchema,
    LessonCreateSchema, LessonUpdateSchema, LessonSchema,
    AssignmentCreateSchema, AssignmentUpdateSchema, AssignmentSchema,
    EnrollmentCreateSchema, EnrollmentSchema,
    LessonProgressSchema, LessonProgressUpdateSchema,
    AssignmentSubmissionCreateSchema, AssignmentSubmissionSchema,
    AssignmentSubmissionGradeSchema
)
from src.common.exceptions.base import BaseException
from src.common.enums.course import CourseLevel, CourseStatus
from src.common.enums.lesson import LessonType, LessonStatus, AssignmentType
from src.common.enums.enrollment import EnrollmentStatus, ProgressStatus


class CourseService:
    """Сервис для управления курсами."""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create(self, body: CourseCreateSchema) -> CourseSchema:
        course = Course.create(
            title=body.title,
            description=body.description,
            author_id=body.author_id,
            level=body.level or CourseLevel.beginner,
            price=body.price,
            duration_hours=body.duration_hours,
            tags=body.tags or [],
            image_url=body.image_url,
            max_students=body.max_students
        )

        async with self.uow:
            await self.uow.courses.create(course)

        return CourseSchema.model_validate(course.__dict__)

    async def get_by_id(self, course_id: UUID) -> CourseSchema:
        async with self.uow:
            course = await self.uow.courses.get_by_id(course_id)
            if not course:
                raise BaseException(f"Course {course_id} not found")

        return CourseSchema.model_validate(course.__dict__)

    async def list(self, limit: int = 10, offset: int = 0) -> List[CourseSchema]:
        async with self.uow:
            courses = await self.uow.courses.list(limit, offset)

        return [CourseSchema.model_validate(c.__dict__) for c in courses]

    async def update(self, course_id: UUID, body: CourseUpdateSchema) -> CourseSchema:
        async with self.uow:
            course = await self.uow.courses.get_by_id(course_id)
            if not course:
                raise BaseException(f"Course {course_id} not found")

            # Обновляем поля
            if body.title is not None:
                course.title = body.title
            if body.description is not None:
                course.description = body.description
            if body.level is not None:
                course.level = body.level
            if body.status is not None:
                course.status = body.status
            if body.price is not None:
                course.price = body.price
                course.is_free = body.price == 0
            if body.duration_hours is not None:
                course.duration_hours = body.duration_hours
            if body.tags is not None:
                course.tags = body.tags
            if body.image_url is not None:
                course.image_url = body.image_url
            if body.max_students is not None:
                course.max_students = body.max_students

            course.updated_at = datetime.utcnow()
            await self.uow.courses.update(course)

        return CourseSchema.model_validate(course.__dict__)

    async def delete(self, course_id: UUID) -> bool:
        async with self.uow:
            return await self.uow.courses.delete(course_id)

    async def get_by_author(self, author_id: UUID, limit: int = 10, offset: int = 0) -> List[CourseSchema]:
        async with self.uow:
            courses = await self.uow.courses.get_by_author(author_id, limit, offset)

        return [CourseSchema.model_validate(c.__dict__) for c in courses]


class LessonService:
    """Сервис для управления уроками."""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create(self, body: LessonCreateSchema) -> LessonSchema:
        lesson = Lesson.create(
            course_id=body.course_id,
            title=body.title,
            content=body.content,
            lesson_type=body.lesson_type,
            order_index=body.order_index,
            duration_minutes=body.duration_minutes,
            video_url=body.video_url,
            materials=body.materials or [],
            is_free_preview=body.is_free_preview or False
        )

        async with self.uow:
            await self.uow.lessons.create(lesson)

        return LessonSchema.model_validate(lesson.__dict__)

    async def get_by_id(self, lesson_id: UUID) -> LessonSchema:
        async with self.uow:
            lesson = await self.uow.lessons.get_by_id(lesson_id)
            if not lesson:
                raise BaseException(f"Lesson {lesson_id} not found")

        return LessonSchema.model_validate(lesson.__dict__)

    async def get_by_course_id(self, course_id: UUID) -> List[LessonSchema]:
        async with self.uow:
            lessons = await self.uow.lessons.get_by_course_id(course_id)

        return [LessonSchema.model_validate(l.__dict__) for l in lessons]

    async def update(self, lesson_id: UUID, body: LessonUpdateSchema) -> LessonSchema:
        async with self.uow:
            lesson = await self.uow.lessons.get_by_id(lesson_id)
            if not lesson:
                raise BaseException(f"Lesson {lesson_id} not found")

            # Обновляем поля
            if body.title is not None:
                lesson.title = body.title
            if body.content is not None:
                lesson.content = body.content
            if body.lesson_type is not None:
                lesson.lesson_type = body.lesson_type
            if body.status is not None:
                lesson.status = body.status
            if body.order_index is not None:
                lesson.order_index = body.order_index
            if body.duration_minutes is not None:
                lesson.duration_minutes = body.duration_minutes
            if body.video_url is not None:
                lesson.video_url = body.video_url
            if body.materials is not None:
                lesson.materials = body.materials
            if body.is_free_preview is not None:
                lesson.is_free_preview = body.is_free_preview

            lesson.updated_at = datetime.utcnow()
            await self.uow.lessons.update(lesson)

        return LessonSchema.model_validate(lesson.__dict__)

    async def delete(self, lesson_id: UUID) -> bool:
        async with self.uow:
            return await self.uow.lessons.delete(lesson_id)


class AssignmentService:
    """Сервис для управления заданиями."""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create(self, body: AssignmentCreateSchema) -> AssignmentSchema:
        assignment = Assignment.create(
            lesson_id=body.lesson_id,
            title=body.title,
            description=body.description,
            assignment_type=body.assignment_type,
            questions=body.questions,
            max_score=body.max_score,
            passing_score=body.passing_score,
            time_limit_minutes=body.time_limit_minutes,
            is_required=body.is_required
        )

        async with self.uow:
            await self.uow.assignments.create(assignment)

        return AssignmentSchema.model_validate(assignment.__dict__)

    async def get_by_id(self, assignment_id: UUID) -> AssignmentSchema:
        async with self.uow:
            assignment = await self.uow.assignments.get_by_id(assignment_id)
            if not assignment:
                raise BaseException(f"Assignment {assignment_id} not found")

        return AssignmentSchema.model_validate(assignment.__dict__)

    async def get_by_lesson_id(self, lesson_id: UUID) -> List[AssignmentSchema]:
        async with self.uow:
            assignments = await self.uow.assignments.get_by_lesson_id(lesson_id)

        return [AssignmentSchema.model_validate(a.__dict__) for a in assignments]

    async def update(self, assignment_id: UUID, body: AssignmentUpdateSchema) -> AssignmentSchema:
        async with self.uow:
            assignment = await self.uow.assignments.get_by_id(assignment_id)
            if not assignment:
                raise BaseException(f"Assignment {assignment_id} not found")

            # Обновляем поля
            if body.title is not None:
                assignment.title = body.title
            if body.description is not None:
                assignment.description = body.description
            if body.assignment_type is not None:
                assignment.assignment_type = body.assignment_type
            if body.questions is not None:
                assignment.questions = body.questions
            if body.max_score is not None:
                assignment.max_score = body.max_score
            if body.passing_score is not None:
                assignment.passing_score = body.passing_score
            if body.time_limit_minutes is not None:
                assignment.time_limit_minutes = body.time_limit_minutes
            if body.is_required is not None:
                assignment.is_required = body.is_required

            assignment.updated_at = datetime.utcnow()
            await self.uow.assignments.update(assignment)

        return AssignmentSchema.model_validate(assignment.__dict__)

    async def delete(self, assignment_id: UUID) -> bool:
        async with self.uow:
            return await self.uow.assignments.delete(assignment_id)


class EnrollmentService:
    """Сервис для управления записями на курсы."""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def enroll(self, body: EnrollmentCreateSchema) -> EnrollmentSchema:
        async with self.uow:
            # Проверяем, не записан ли уже пользователь на курс
            existing_enrollment = await self.uow.enrollments.get_by_user_and_course(
                body.user_id, body.course_id
            )
            if existing_enrollment:
                raise BaseException("User already enrolled in this course")

            enrollment = Enrollment.create(
                user_id=body.user_id,
                course_id=body.course_id
            )

            await self.uow.enrollments.create(enrollment)

        return EnrollmentSchema.model_validate(enrollment.__dict__)

    async def get_by_id(self, enrollment_id: UUID) -> EnrollmentSchema:
        async with self.uow:
            enrollment = await self.uow.enrollments.get_by_id(enrollment_id)
            if not enrollment:
                raise BaseException(f"Enrollment {enrollment_id} not found")

        return EnrollmentSchema.model_validate(enrollment.__dict__)

    async def get_by_user_id(self, user_id: UUID, limit: int = 10, offset: int = 0) -> List[EnrollmentSchema]:
        async with self.uow:
            enrollments = await self.uow.enrollments.get_by_user_id(user_id, limit, offset)

        return [EnrollmentSchema.model_validate(e.__dict__) for e in enrollments]

    async def get_by_course_id(self, course_id: UUID, limit: int = 10, offset: int = 0) -> List[EnrollmentSchema]:
        async with self.uow:
            enrollments = await self.uow.enrollments.get_by_course_id(course_id, limit, offset)

        return [EnrollmentSchema.model_validate(e.__dict__) for e in enrollments]

    async def update_progress(self, enrollment_id: UUID, progress_percentage: float) -> EnrollmentSchema:
        async with self.uow:
            enrollment = await self.uow.enrollments.get_by_id(enrollment_id)
            if not enrollment:
                raise BaseException(f"Enrollment {enrollment_id} not found")

            enrollment.progress_percentage = progress_percentage
            enrollment.last_accessed_at = datetime.utcnow()

            # Если курс завершен
            if progress_percentage >= 100.0:
                enrollment.status = EnrollmentStatus.completed
                enrollment.completed_at = datetime.utcnow()

            await self.uow.enrollments.update(enrollment)

        return EnrollmentSchema.model_validate(enrollment.__dict__)


class LessonProgressService:
    """Сервис для управления прогрессом по урокам."""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def start_lesson(self, enrollment_id: UUID, lesson_id: UUID) -> LessonProgressSchema:
        async with self.uow:
            # Проверяем, есть ли уже прогресс
            progress = await self.uow.lesson_progress.get_by_enrollment_and_lesson(
                enrollment_id, lesson_id
            )

            if not progress:
                progress = LessonProgress.create(enrollment_id, lesson_id)
                await self.uow.lesson_progress.create(progress)

            # Обновляем статус на "начат"
            if progress.status == ProgressStatus.not_started:
                progress.status = ProgressStatus.started
                progress.started_at = datetime.utcnow()
                await self.uow.lesson_progress.update(progress)

        return LessonProgressSchema.model_validate(progress.__dict__)

    async def complete_lesson(self, enrollment_id: UUID, lesson_id: UUID) -> LessonProgressSchema:
        async with self.uow:
            progress = await self.uow.lesson_progress.get_by_enrollment_and_lesson(
                enrollment_id, lesson_id
            )

            if not progress:
                raise BaseException("Lesson progress not found")

            progress.status = ProgressStatus.completed
            progress.completed_at = datetime.utcnow()

            await self.uow.lesson_progress.update(progress)

        return LessonProgressSchema.model_validate(progress.__dict__)

    async def update_time_spent(self, enrollment_id: UUID, lesson_id: UUID, additional_minutes: int) -> LessonProgressSchema:
        async with self.uow:
            progress = await self.uow.lesson_progress.get_by_enrollment_and_lesson(
                enrollment_id, lesson_id
            )

            if not progress:
                raise BaseException("Lesson progress not found")

            progress.time_spent_minutes += additional_minutes
            await self.uow.lesson_progress.update(progress)

        return LessonProgressSchema.model_validate(progress.__dict__)

    async def get_by_enrollment_id(self, enrollment_id: UUID) -> List[LessonProgressSchema]:
        async with self.uow:
            progress_records = await self.uow.lesson_progress.get_by_enrollment_id(enrollment_id)

        return [LessonProgressSchema.model_validate(p.__dict__) for p in progress_records]


class AssignmentSubmissionService:
    """Сервис для управления ответами на задания."""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def submit(self, body: AssignmentSubmissionCreateSchema) -> AssignmentSubmissionSchema:
        async with self.uow:
            # Получаем количество попыток
            existing_submissions = await self.uow.assignment_submissions.get_by_assignment_and_enrollment(
                body.assignment_id, body.enrollment_id
            )

            attempt_number = len(existing_submissions) + 1

            submission = AssignmentSubmission.create(
                assignment_id=body.assignment_id,
                enrollment_id=body.enrollment_id,
                answers=body.answers,
                attempt_number=attempt_number
            )

            await self.uow.assignment_submissions.create(submission)

        return AssignmentSubmissionSchema.model_validate(submission.__dict__)

    async def grade(self, submission_id: UUID, body: AssignmentSubmissionGradeSchema) -> AssignmentSubmissionSchema:
        async with self.uow:
            submission = await self.uow.assignment_submissions.get_by_id(submission_id)
            if not submission:
                raise BaseException(f"Submission {submission_id} not found")

            submission.score = body.score
            submission.feedback = body.feedback
            submission.status = body.status
            submission.graded_at = datetime.utcnow()

            await self.uow.assignment_submissions.update(submission)

        return AssignmentSubmissionSchema.model_validate(submission.__dict__)

    async def get_by_id(self, submission_id: UUID) -> AssignmentSubmissionSchema:
        async with self.uow:
            submission = await self.uow.assignment_submissions.get_by_id(submission_id)
            if not submission:
                raise BaseException(f"Submission {submission_id} not found")

        return AssignmentSubmissionSchema.model_validate(submission.__dict__)

    async def get_by_enrollment_id(self, enrollment_id: UUID) -> List[AssignmentSubmissionSchema]:
        async with self.uow:
            submissions = await self.uow.assignment_submissions.get_by_enrollment_id(enrollment_id)

        return [AssignmentSubmissionSchema.model_validate(s.__dict__) for s in submissions]

    async def get_latest_by_assignment(self, assignment_id: UUID, enrollment_id: UUID) -> Optional[AssignmentSubmissionSchema]:
        async with self.uow:
            submission = await self.uow.assignment_submissions.get_latest_by_assignment_and_enrollment(
                assignment_id, enrollment_id
            )

        return AssignmentSubmissionSchema.model_validate(submission.__dict__) if submission else None

from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional

from .models import (
    Course, Lesson, Assignment, Enrollment,
    LessonProgress, AssignmentSubmission
)


class AbstractCourseRepository(ABC):
    """Абстрактный репозиторий для курсов."""

    @abstractmethod
    async def get_by_id(self, course_id: UUID) -> Optional[Course]:
        ...

    @abstractmethod
    async def list(self, limit: int, offset: int) -> List[Course]:
        ...

    @abstractmethod
    async def create(self, course: Course) -> None:
        ...

    @abstractmethod
    async def update(self, course: Course) -> None:
        ...

    @abstractmethod
    async def delete(self, course_id: UUID) -> bool:
        ...

    @abstractmethod
    async def get_by_author(self, author_id: UUID, limit: int, offset: int) -> List[Course]:
        ...


class AbstractLessonRepository(ABC):
    """Абстрактный репозиторий для уроков."""

    @abstractmethod
    async def get_by_id(self, lesson_id: UUID) -> Optional[Lesson]:
        ...

    @abstractmethod
    async def get_by_course_id(self, course_id: UUID) -> List[Lesson]:
        ...

    @abstractmethod
    async def create(self, lesson: Lesson) -> None:
        ...

    @abstractmethod
    async def update(self, lesson: Lesson) -> None:
        ...

    @abstractmethod
    async def delete(self, lesson_id: UUID) -> bool:
        ...


class AbstractAssignmentRepository(ABC):
    """Абстрактный репозиторий для заданий."""

    @abstractmethod
    async def get_by_id(self, assignment_id: UUID) -> Optional[Assignment]:
        ...

    @abstractmethod
    async def get_by_lesson_id(self, lesson_id: UUID) -> List[Assignment]:
        ...

    @abstractmethod
    async def create(self, assignment: Assignment) -> None:
        ...

    @abstractmethod
    async def update(self, assignment: Assignment) -> None:
        ...

    @abstractmethod
    async def delete(self, assignment_id: UUID) -> bool:
        ...


class AbstractEnrollmentRepository(ABC):
    """Абстрактный репозиторий для записей на курсы."""

    @abstractmethod
    async def get_by_id(self, enrollment_id: UUID) -> Optional[Enrollment]:
        ...

    @abstractmethod
    async def get_by_user_and_course(self, user_id: UUID, course_id: UUID) -> Optional[Enrollment]:
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int, offset: int) -> List[Enrollment]:
        ...

    @abstractmethod
    async def get_by_course_id(self, course_id: UUID, limit: int, offset: int) -> List[Enrollment]:
        ...

    @abstractmethod
    async def create(self, enrollment: Enrollment) -> None:
        ...

    @abstractmethod
    async def update(self, enrollment: Enrollment) -> None:
        ...

    @abstractmethod
    async def delete(self, enrollment_id: UUID) -> bool:
        ...


class AbstractLessonProgressRepository(ABC):
    """Абстрактный репозиторий для прогресса по урокам."""

    @abstractmethod
    async def get_by_id(self, progress_id: UUID) -> Optional[LessonProgress]:
        ...

    @abstractmethod
    async def get_by_enrollment_and_lesson(self, enrollment_id: UUID, lesson_id: UUID) -> Optional[LessonProgress]:
        ...

    @abstractmethod
    async def get_by_enrollment_id(self, enrollment_id: UUID) -> List[LessonProgress]:
        ...

    @abstractmethod
    async def create(self, progress: LessonProgress) -> None:
        ...

    @abstractmethod
    async def update(self, progress: LessonProgress) -> None:
        ...


class AbstractAssignmentSubmissionRepository(ABC):
    """Абстрактный репозиторий для ответов на задания."""

    @abstractmethod
    async def get_by_id(self, submission_id: UUID) -> Optional[AssignmentSubmission]:
        ...

    @abstractmethod
    async def get_by_assignment_and_enrollment(self, assignment_id: UUID, enrollment_id: UUID) -> List[AssignmentSubmission]:
        ...

    @abstractmethod
    async def get_by_enrollment_id(self, enrollment_id: UUID) -> List[AssignmentSubmission]:
        ...

    @abstractmethod
    async def create(self, submission: AssignmentSubmission) -> None:
        ...

    @abstractmethod
    async def update(self, submission: AssignmentSubmission) -> None:
        ...

    @abstractmethod
    async def get_latest_by_assignment_and_enrollment(self, assignment_id: UUID, enrollment_id: UUID) -> Optional[AssignmentSubmission]:
        ...

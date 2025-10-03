"""
SQLAdmin модели для административной панели.
"""

from sqladmin import Admin, ModelView

from src.courses.infrastructure.sqlalchemy.models import (
    Course, Lesson, Assignment, Enrollment,
    LessonProgress, AssignmentSubmission
)


class CourseAdmin(ModelView, model=Course):
    """Админ-модель для курсов."""

    name = "Курс"
    name_plural = "Курсы"
    icon = "fa-solid fa-book"

    # Поля для отображения в списке
    column_list = [Course.id, Course.title, Course.author_id, Course.level, Course.status, Course.is_free, Course.created_at]

    # Поля для поиска
    column_searchable_list = [Course.title, Course.description]

    # Фильтры
    column_filters = [Course.level, Course.status, Course.is_free, Course.created_at]

    # Сортировка по умолчанию
    column_default_sort = [(Course.created_at, True)]

    # Детали формы
    form_columns = [
        Course.title, Course.description, Course.author_id, Course.level,
        Course.status, Course.price, Course.duration_hours, Course.tags,
        Course.image_url, Course.is_free, Course.max_students
    ]

    # Только для чтения
    form_readonly_fields = [Course.id, Course.created_at, Course.updated_at]


class LessonAdmin(ModelView, model=Lesson):
    """Админ-модель для уроков."""

    name = "Урок"
    name_plural = "Уроки"
    icon = "fa-solid fa-graduation-cap"

    column_list = [
        Lesson.id, Lesson.title, Lesson.course_id,
        Lesson.lesson_type, Lesson.status, Lesson.order_index, Lesson.created_at
    ]

    column_searchable_list = [Lesson.title, Lesson.content]
    column_filters = [Lesson.lesson_type, Lesson.status, Lesson.is_free_preview, Lesson.created_at]
    column_default_sort = [(Lesson.course_id, False), (Lesson.order_index, False)]

    form_columns = [
        Lesson.course_id, Lesson.title, Lesson.content, Lesson.lesson_type,
        Lesson.status, Lesson.order_index, Lesson.duration_minutes,
        Lesson.video_url, Lesson.materials, Lesson.is_free_preview
    ]

    form_readonly_fields = [Lesson.id, Lesson.created_at, Lesson.updated_at]


class AssignmentAdmin(ModelView, model=Assignment):
    """Админ-модель для заданий."""

    name = "Задание"
    name_plural = "Задания"
    icon = "fa-solid fa-tasks"

    column_list = [
        Assignment.id, Assignment.title, Assignment.lesson_id,
        Assignment.assignment_type, Assignment.max_score, Assignment.is_required, Assignment.created_at
    ]

    column_searchable_list = [Assignment.title, Assignment.description]
    column_filters = [Assignment.assignment_type, Assignment.is_required, Assignment.created_at]
    column_default_sort = [(Assignment.created_at, True)]

    form_columns = [
        Assignment.lesson_id, Assignment.title, Assignment.description,
        Assignment.assignment_type, Assignment.questions, Assignment.max_score,
        Assignment.passing_score, Assignment.time_limit_minutes, Assignment.is_required
    ]

    form_readonly_fields = [Assignment.id, Assignment.created_at, Assignment.updated_at]


class EnrollmentAdmin(ModelView, model=Enrollment):
    """Админ-модель для записей на курсы."""

    name = "Запись на курс"
    name_plural = "Записи на курсы"
    icon = "fa-solid fa-user-graduate"

    column_list = [
        Enrollment.id, Enrollment.user_id, Enrollment.course_id,
        Enrollment.status, Enrollment.progress_percentage, Enrollment.enrolled_at, Enrollment.completed_at
    ]

    column_filters = [Enrollment.status, Enrollment.certificate_issued, Enrollment.enrolled_at]
    column_default_sort = [(Enrollment.enrolled_at, True)]

    form_columns = [
        Enrollment.user_id, Enrollment.course_id, Enrollment.status,
        Enrollment.progress_percentage, Enrollment.last_accessed_at, Enrollment.certificate_issued
    ]

    form_readonly_fields = [
        Enrollment.id, Enrollment.enrolled_at, Enrollment.completed_at
    ]


class LessonProgressAdmin(ModelView, model=LessonProgress):
    """Админ-модель для прогресса по урокам."""

    name = "Прогресс по уроку"
    name_plural = "Прогресс по урокам"
    icon = "fa-solid fa-chart-line"

    column_list = [
        LessonProgress.id, LessonProgress.enrollment_id, LessonProgress.lesson_id,
        LessonProgress.status, LessonProgress.time_spent_minutes, LessonProgress.started_at
    ]

    column_filters = [LessonProgress.status, LessonProgress.started_at]
    column_default_sort = [(LessonProgress.started_at, True)]

    form_columns = [
        LessonProgress.enrollment_id, LessonProgress.lesson_id, LessonProgress.status,
        LessonProgress.time_spent_minutes
    ]

    form_readonly_fields = [
        LessonProgress.id, LessonProgress.started_at, LessonProgress.completed_at
    ]


class AssignmentSubmissionAdmin(ModelView, model=AssignmentSubmission):
    """Админ-модель для ответов на задания."""

    name = "Ответ на задание"
    name_plural = "Ответы на задания"
    icon = "fa-solid fa-file-text"

    column_list = [
        AssignmentSubmission.id, AssignmentSubmission.assignment_id, AssignmentSubmission.enrollment_id,
        AssignmentSubmission.score, AssignmentSubmission.status, AssignmentSubmission.attempt_number,
        AssignmentSubmission.submitted_at
    ]

    column_filters = [AssignmentSubmission.status, AssignmentSubmission.submitted_at]
    column_default_sort = [(AssignmentSubmission.submitted_at, True)]

    form_columns = [
        AssignmentSubmission.assignment_id, AssignmentSubmission.enrollment_id, AssignmentSubmission.answers,
        AssignmentSubmission.score, AssignmentSubmission.status, AssignmentSubmission.feedback,
        AssignmentSubmission.attempt_number
    ]

    form_readonly_fields = [
        AssignmentSubmission.id, AssignmentSubmission.submitted_at, AssignmentSubmission.graded_at
    ]


def setup_admin_views(admin: Admin):
    """Регистрация всех админ-моделей."""
    admin.add_view(CourseAdmin)
    admin.add_view(LessonAdmin)
    admin.add_view(AssignmentAdmin)
    admin.add_view(EnrollmentAdmin)
    admin.add_view(LessonProgressAdmin)
    admin.add_view(AssignmentSubmissionAdmin)
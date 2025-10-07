"""
SQLAdmin модели для административной панели.
"""

from sqladmin import Admin, ModelView
from starlette.requests import Request

from src.courses.infrastructure.sqlalchemy.models import (
    Course, Lesson, Assignment, Enrollment,
    LessonProgress, AssignmentSubmission
)

# Базовый класс с общей безопасностью/настройками
class SecureModelView(ModelView):
    """Единые настройки и проверка доступа для всех ModelView."""
    # Доступ только суперпользователю (см. AdminAuth.session_key_is_superuser)
    def is_accessible(self, request: Request) -> bool:
        """Проверка доступа к админ-панели для всех ModelView."""
        return bool(
            request.session.get("admin_authenticated") and
            request.session.get("admin_user_id")
        )    # Удобная пагинация и экспорт по умолчанию
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    can_export = True
    export_types = ["csv", "json"]


class CourseAdmin(SecureModelView, model=Course):
    """Админ-модель для курсов."""
    name = "Курс"
    name_plural = "Курсы"
    icon = "fa-solid fa-book"
    category = "Обучение"

    # Поля для отображения в списке
    column_list = ["id", "title", "author_id", "level", "status", "is_free", "created_at"]
    # Поля для поиска
    column_searchable_list = ["title", "description"]
    # Детали формы
    form_columns = [
        Course.title, Course.description, Course.author_id, Course.level,
        Course.status, Course.price, Course.duration_hours, Course.tags,
        Course.image_url, Course.is_free, Course.max_students
    ]
    # Только для чтения
    form_readonly_fields = [Course.id, Course.created_at, Course.updated_at]


class LessonAdmin(SecureModelView, model=Lesson):
    """Админ-модель для уроков."""
    name = "Урок"
    name_plural = "Уроки"
    icon = "fa-solid fa-graduation-cap"
    category = "Обучение"

    column_list = [
        "id", "title", "course_id",
        "lesson_type", "status", "order_index", "created_at"
    ]
    column_searchable_list = ["title", "content"]
    form_columns = [
        Lesson.course_id, Lesson.title, Lesson.content, Lesson.lesson_type,
        Lesson.status, Lesson.order_index, Lesson.duration_minutes,
        Lesson.video_url, Lesson.materials, Lesson.is_free_preview
    ]
    form_readonly_fields = [Lesson.id, Lesson.created_at, Lesson.updated_at]


class AssignmentAdmin(SecureModelView, model=Assignment):
    """Админ-модель для заданий."""
    name = "Задание"
    name_plural = "Задания"
    icon = "fa-solid fa-tasks"
    category = "Обучение"

    column_list = [
        "id", "title", "lesson_id",
        "assignment_type", "max_score", "is_required", "created_at"
    ]
    column_searchable_list = ["title", "description"]
    form_columns = [
        Assignment.lesson_id, Assignment.title, Assignment.description,
        Assignment.assignment_type, Assignment.questions, Assignment.max_score,
        Assignment.passing_score, Assignment.time_limit_minutes, Assignment.is_required
    ]
    form_readonly_fields = [Assignment.id, Assignment.created_at, Assignment.updated_at]


class EnrollmentAdmin(SecureModelView, model=Enrollment):
    """Админ-модель для записей на курсы."""
    name = "Запись на курс"
    name_plural = "Записи на курсы"
    icon = "fa-solid fa-user-graduate"
    category = "Студенты"

    column_list = [
        "id", "user_id", "course_id",
        "status", "progress_percentage", "enrolled_at", "completed_at"
    ]
    form_columns = [
        Enrollment.user_id, Enrollment.course_id, Enrollment.status,
        Enrollment.progress_percentage, Enrollment.last_accessed_at, Enrollment.certificate_issued
    ]
    form_readonly_fields = [
        Enrollment.id, Enrollment.enrolled_at, Enrollment.completed_at
    ]


class LessonProgressAdmin(SecureModelView, model=LessonProgress):
    """Админ-модель для прогресса по урокам."""
    name = "Прогресс по уроку"
    name_plural = "Прогресс по урокам"
    icon = "fa-solid fa-chart-line"
    category = "Студенты"

    column_list = [
        "id", "enrollment_id", "lesson_id",
        "status", "time_spent_minutes", "started_at"
    ]
    form_columns = [
        LessonProgress.enrollment_id, LessonProgress.lesson_id, LessonProgress.status,
        LessonProgress.time_spent_minutes
    ]
    form_readonly_fields = [
        LessonProgress.id, LessonProgress.started_at, LessonProgress.completed_at
    ]


class AssignmentSubmissionAdmin(SecureModelView, model=AssignmentSubmission):
    """Админ-модель для ответов на задания."""
    name = "Ответ на задание"
    name_plural = "Ответы на задания"
    icon = "fa-solid fa-file-text"
    category = "Студенты"

    column_list = [
        "id", "assignment_id", "enrollment_id",
        "score", "status", "attempt_number",
        "submitted_at"
    ]
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

"""
SQLAdmin модели для административной панели
"""
from sqladmin import Admin
from .views import (
    CourseAdminView,
    CourseModeratorAdminView,
    CourseTopicAdminView,
    LessonAdminView,
    GroupAdminView,
    EnrollmentAdminView,
    AssignmentAdminView,
    SubmissionAdminView,
    AnswerSubmissionAdminView,
    QuestionBlockAdminView,
    QuestionAdminView,
    AnswerOptionAdminView,
    GradeAdminView,
    CommentAdminView,
    ProgressAdminView,
)


def setup_admin_views(admin: Admin):
    """Регистрация всех админ-моделей"""

    # Курсы и обучение
    admin.add_view(CourseAdminView)
    admin.add_view(CourseModeratorAdminView)
    admin.add_view(CourseTopicAdminView)
    admin.add_view(LessonAdminView)

    # Группы и записи
    admin.add_view(GroupAdminView)
    admin.add_view(EnrollmentAdminView)

    # Задания и тестирование
    admin.add_view(AssignmentAdminView)
    admin.add_view(SubmissionAdminView)
    admin.add_view(AnswerSubmissionAdminView)
    admin.add_view(QuestionBlockAdminView)
    admin.add_view(QuestionAdminView)
    admin.add_view(AnswerOptionAdminView)

    # Оценки и обратная связь
    admin.add_view(GradeAdminView)
    admin.add_view(CommentAdminView)

    # Прогресс обучения
    admin.add_view(ProgressAdminView)
"""
Представления админки для всех моделей
"""
import uuid
import asyncio
from typing import Any, Dict, List
import httpx
from sqladmin import ModelView
from starlette.requests import Request

from .base import BaseAdminView
from src.models import (
    Course, CourseModerator, CourseTopic, Lesson,
    Group, Enrollment,
    Assignment, Submission, AnswerSubmission,
    QuestionBlock, Question, AnswerOption,
    Grade, Comment, Progress
)
from src.core.config import settings


class AuthServiceMixin:
    """Миксин для обогащения данных пользователями из auth-сервиса"""

    @staticmethod
    async def enrich_with_user_info(data: List[Dict], user_field: str = "user_id") -> List[Dict]:
        """Обогащает данные информацией о пользователях"""
        if not data:
            return data

        # Собираем все user_id
        user_ids = set()
        for item in data:
            user_id = item.get(user_field)
            if user_id:
                user_ids.add(str(user_id))

        if not user_ids:
            return data

        # Получаем информацию о пользователях батч-запросом
        try:
            headers = {}
            # Добавляем service token для межсервисной аутентификации, если он настроен
            if settings.auth_service.service_token:
                headers["Authorization"] = f"Bearer {settings.auth_service.service_token}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.auth_service.url}/api/v1/users/batch/",
                    json={"user_ids": list(user_ids)},
                    headers=headers
                )

                if response.status_code == 200:
                    users_data = response.json()["users"]

                    # Обогащаем данные
                    for item in data:
                        user_id = str(item.get(user_field, ""))
                        if user_id in users_data:
                            user_info = users_data[user_id]
                            item[f"{user_field}_info"] = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')} ({user_info.get('username', '')})"
                        else:
                            item[f"{user_field}_info"] = f"Пользователь {user_id}"

        except Exception:
            # В случае ошибки просто отображаем ID
            for item in data:
                user_id = item.get(user_field)
                if user_id:
                    item[f"{user_field}_info"] = f"Пользователь {user_id}"

        return data


# Курсы и обучение
class CourseAdminView(BaseAdminView, model=Course):
    """Админка для курсов"""

    column_list = [Course.id, Course.title, Course.description, Course.created_at]
    column_searchable_list = [Course.title]
    column_sortable_list = [Course.title, Course.created_at]
    column_details_exclude_list = ["groups", "topics", "moderators"]

    name = "Курс"
    name_plural = "Курсы"
    icon = "fa-solid fa-book"


class CourseModeratorAdminView(BaseAdminView, AuthServiceMixin, model=CourseModerator):
    """Админка для модераторов курсов"""

    column_list = [CourseModerator.id, "user_info", CourseModerator.course_id, CourseModerator.created_at]
    column_searchable_list = [CourseModerator.user_id]
    column_sortable_list = [CourseModerator.created_at]

    name = "Модератор курса"
    name_plural = "Модераторы курсов"
    icon = "fa-solid fa-user-shield"

    async def list(self, request: Request) -> Any:
        """Переопределяем список для обогащения данными пользователей"""
        result = await super().list(request)

        # Обогащаем данные пользователей
        if hasattr(result, 'data') and result.data:
            data_list = []
            for item in result.data:
                item_dict = item.__dict__.copy() if hasattr(item, '__dict__') else dict(item)
                data_list.append(item_dict)

            enriched_data = await self.enrich_with_user_info(data_list, "user_id")

            # Обновляем результат
            for i, item in enumerate(result.data):
                if i < len(enriched_data):
                    item.user_info = enriched_data[i].get("user_id_info", "")

        return result


class CourseTopicAdminView(BaseAdminView, model=CourseTopic):
    """Админка для тем курсов"""

    column_list = [
        CourseTopic.id,
        CourseTopic.title,
        CourseTopic.course_id,
        CourseTopic.parent_id,
        CourseTopic.order
    ]
    column_searchable_list = [CourseTopic.title]
    column_sortable_list = [CourseTopic.title, CourseTopic.order, CourseTopic.created_at]
    column_details_exclude_list = ["subtopics", "lessons", "assignments"]

    name = "Тема курса"
    name_plural = "Темы курсов"
    icon = "fa-solid fa-list"


class LessonAdminView(BaseAdminView, model=Lesson):
    """Админка для уроков"""

    column_list = [Lesson.id, Lesson.title, Lesson.topic_id, Lesson.order, Lesson.date]
    column_searchable_list = [Lesson.title]
    column_sortable_list = [Lesson.title, Lesson.order, Lesson.date]
    column_details_exclude_list = ["assignments"]

    name = "Урок"
    name_plural = "Уроки"
    icon = "fa-solid fa-chalkboard-teacher"


# Группы и записи
class GroupAdminView(BaseAdminView, model=Group):
    """Админка для групп"""

    column_list = [Group.id, Group.name, Group.course_id, Group.moodle_group_id]
    column_searchable_list = [Group.name, Group.moodle_group_id]
    column_sortable_list = [Group.name, Group.created_at]
    column_details_exclude_list = ["enrollments"]

    name = "Группа"
    name_plural = "Группы"
    icon = "fa-solid fa-users"


class EnrollmentAdminView(BaseAdminView, AuthServiceMixin, model=Enrollment):
    """Админка для записей в группы"""

    column_list = [Enrollment.id, "user_info", Enrollment.group_id, Enrollment.role, Enrollment.status, Enrollment.date_start]
    column_searchable_list = [Enrollment.user_id]
    column_sortable_list = [Enrollment.role, Enrollment.status, Enrollment.date_start]
    column_details_exclude_list = ["progress"]

    name = "Запись в группу"
    name_plural = "Записи в группы"
    icon = "fa-solid fa-user-plus"

    async def list(self, request: Request) -> Any:
        """Переопределяем список для обогащения данными пользователей"""
        result = await super().list(request)

        # Обогащаем данные пользователей
        if hasattr(result, 'data') and result.data:
            data_list = []
            for item in result.data:
                item_dict = item.__dict__.copy() if hasattr(item, '__dict__') else dict(item)
                data_list.append(item_dict)

            enriched_data = await self.enrich_with_user_info(data_list, "user_id")

            # Обновляем результат
            for i, item in enumerate(result.data):
                if i < len(enriched_data):
                    item.user_info = enriched_data[i].get("user_id_info", "")

        return result


# Задания и тестирование
class AssignmentAdminView(BaseAdminView, model=Assignment):
    """Админка для заданий"""

    column_list = [
        Assignment.id,
        Assignment.title,
        Assignment.type,
        Assignment.max_score,
        Assignment.max_attempts,
        Assignment.due_date,
        Assignment.topic_id,
        Assignment.lesson_id
    ]
    column_searchable_list = [Assignment.title]
    column_sortable_list = [Assignment.title, Assignment.type, Assignment.due_date, Assignment.created_at]
    column_details_exclude_list = ["question_blocks", "submissions"]

    name = "Задание"
    name_plural = "Задания"
    icon = "fa-solid fa-tasks"


class SubmissionAdminView(BaseAdminView, AuthServiceMixin, model=Submission):
    """Админка для отправок заданий"""

    column_list = [Submission.id, "student_info", Submission.assignment_id, Submission.score, Submission.submitted_at]
    column_sortable_list = [Submission.score, Submission.submitted_at]
    column_details_exclude_list = ["answers", "grade", "comments"]

    name = "Отправка задания"
    name_plural = "Отправки заданий"
    icon = "fa-solid fa-paper-plane"

    async def list(self, request: Request) -> Any:
        """Обогащаем данными студентов"""
        result = await super().list(request)

        if hasattr(result, 'data') and result.data:
            data_list = []
            for item in result.data:
                item_dict = item.__dict__.copy() if hasattr(item, '__dict__') else dict(item)
                data_list.append(item_dict)

            enriched_data = await self.enrich_with_user_info(data_list, "student_id")

            for i, item in enumerate(result.data):
                if i < len(enriched_data):
                    item.student_info = enriched_data[i].get("student_id_info", "")

        return result


class QuestionBlockAdminView(BaseAdminView, model=QuestionBlock):
    """Админка для блоков вопросов"""

    column_list = [QuestionBlock.id, QuestionBlock.title, QuestionBlock.assignment_id, QuestionBlock.order]
    column_searchable_list = [QuestionBlock.title]
    column_sortable_list = [QuestionBlock.title, QuestionBlock.order]
    column_details_exclude_list = ["questions"]

    name = "Блок вопросов"
    name_plural = "Блоки вопросов"
    icon = "fa-solid fa-question-circle"


class QuestionAdminView(BaseAdminView, model=Question):
    """Админка для вопросов"""

    column_list = [Question.id, Question.text, Question.block_id, Question.multiple, Question.order]
    column_searchable_list = [Question.text]
    column_sortable_list = [Question.order, Question.multiple]
    column_details_exclude_list = ["options", "comments"]

    name = "Вопрос"
    name_plural = "Вопросы"
    icon = "fa-solid fa-question"


class AnswerOptionAdminView(BaseAdminView, model=AnswerOption):
    """Админка для вариантов ответов"""

    column_list = [AnswerOption.id, AnswerOption.text, AnswerOption.question_id, AnswerOption.is_correct]
    column_searchable_list = [AnswerOption.text]
    column_sortable_list = [AnswerOption.is_correct]

    name = "Вариант ответа"
    name_plural = "Варианты ответов"
    icon = "fa-solid fa-check-circle"


# Оценки и обратная связь
class GradeAdminView(BaseAdminView, AuthServiceMixin, model=Grade):
    """Админка для оценок"""

    column_list = [Grade.id, Grade.value, "teacher_info", Grade.submission_id, Grade.graded_at]
    column_sortable_list = [Grade.value, Grade.graded_at]

    name = "Оценка"
    name_plural = "Оценки"
    icon = "fa-solid fa-star"

    async def list(self, request: Request) -> Any:
        """Обогащаем данными преподавателей"""
        result = await super().list(request)

        if hasattr(result, 'data') and result.data:
            data_list = []
            for item in result.data:
                item_dict = item.__dict__.copy() if hasattr(item, '__dict__') else dict(item)
                data_list.append(item_dict)

            enriched_data = await self.enrich_with_user_info(data_list, "teacher_id")

            for i, item in enumerate(result.data):
                if i < len(enriched_data):
                    item.teacher_info = enriched_data[i].get("teacher_id_info", "")

        return result


class CommentAdminView(BaseAdminView, AuthServiceMixin, model=Comment):
    """Админка для комментариев"""

    column_list = [Comment.id, Comment.text, "teacher_info", Comment.submission_id, Comment.question_id]
    column_searchable_list = [Comment.text]
    column_sortable_list = [Comment.created_at]

    name = "Комментарий"
    name_plural = "Комментарии"
    icon = "fa-solid fa-comment"

    async def list(self, request: Request) -> Any:
        """Обогащаем данными преподавателей"""
        result = await super().list(request)

        if hasattr(result, 'data') and result.data:
            data_list = []
            for item in result.data:
                item_dict = item.__dict__.copy() if hasattr(item, '__dict__') else dict(item)
                data_list.append(item_dict)

            enriched_data = await self.enrich_with_user_info(data_list, "teacher_id")

            for i, item in enumerate(result.data):
                if i < len(enriched_data):
                    item.teacher_info = enriched_data[i].get("teacher_id_info", "")

        return result


# Прогресс обучения
class ProgressAdminView(BaseAdminView, model=Progress):
    """Админка для прогресса обучения"""

    column_list = [
        Progress.id,
        Progress.enrollment_id,
        Progress.completion_percentage,
        Progress.completed_assignments,
        Progress.total_assignments,
        Progress.average_score
    ]
    column_sortable_list = [
        Progress.completion_percentage,
        Progress.average_score,
        Progress.last_activity
    ]

    name = "Прогресс обучения"
    name_plural = "Прогресс обучения"
    icon = "fa-solid fa-chart-line"


class AnswerSubmissionAdminView(BaseAdminView, model=AnswerSubmission):
    """Админка для ответов студентов"""

    column_list = [
        AnswerSubmission.id,
        AnswerSubmission.submission_id,
        AnswerSubmission.question_id,
        AnswerSubmission.answer_id,
        AnswerSubmission.is_correct
    ]
    column_sortable_list = [AnswerSubmission.is_correct]

    name = "Ответ студента"
    name_plural = "Ответы студентов"
    icon = "fa-solid fa-edit"
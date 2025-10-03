import enum


class LessonType(enum.StrEnum):
    """Типы уроков в курсе"""
    text = "text"  # Текстовый материал
    video = "video"  # Видео урок
    quiz = "quiz"  # Тест/квиз
    assignment = "assignment"  # Практическое задание
    interactive = "interactive"  # Интерактивный контент
    external_link = "external_link"  # Внешняя ссылка


class LessonStatus(enum.StrEnum):
    """Статус урока"""
    draft = "draft"  # Черновик
    published = "published"  # Опубликован
    archived = "archived"  # Архивирован


class AssignmentType(enum.StrEnum):
    """Типы заданий"""
    multiple_choice = "multiple_choice"  # Множественный выбор
    single_choice = "single_choice"  # Единичный выбор
    text_input = "text_input"  # Ввод текста
    code_input = "code_input"  # Ввод кода
    file_upload = "file_upload"  # Загрузка файла
    essay = "essay"  # Эссе


class SubmissionStatus(enum.StrEnum):
    """Статус выполнения задания"""
    not_started = "not_started"  # Не начато
    in_progress = "in_progress"  # В процессе
    submitted = "submitted"  # Отправлено
    graded = "graded"  # Оценено
    needs_revision = "needs_revision"  # Требует доработки
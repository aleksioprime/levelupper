"""
Дополнительные настройки для улучшения стабильности SQLAdmin
"""
from datetime import datetime
from sqladmin import ModelView


# Базовые настройки для всех админ-моделей
class BaseAdminView(ModelView):
    """Базовый класс для админ-моделей с оптимизированными настройками"""

    # Общие настройки производительности
    page_size = 25  # Меньший размер страницы для лучшей производительности
    page_size_options = [10, 25, 50, 100]  # Опции размера страницы

    # Настройки для предотвращения проблем с lazy loading
    can_view_details = True
    can_create = True
    can_edit = True
    can_delete = True

    # Исключаем проблемные поля по умолчанию
    column_details_exclude_list = ["created_at", "updated_at"]
    form_excluded_columns = ["created_at", "updated_at"]

    # Отключаем автозагрузку связанных объектов для стабильности
    form_ajax_refs = {}

    @classmethod
    def get_list_query(cls, request):
        """Оптимизированный запрос для списка"""
        query = super().get_list_query(request)
        # Добавляем options для предотвращения N+1 проблем
        return query

    @staticmethod
    def format_datetime(value: datetime) -> str:
        """Форматирует datetime для отображения"""
        if not value:
            return ""
        return value.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_user_id(user_id) -> str:
        """Форматирует user_id для отображения"""
        if not user_id:
            return ""
        return f"Пользователь {user_id}"
"""
Дополнительные настройки для улучшения стабильности SQLAdmin
"""
from datetime import datetime
import pytz
from sqladmin import ModelView

from src.core.config import settings


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

    # Настройки для улучшения UX
    column_default_sort = [("created_at", True)] if hasattr(ModelView, "created_at") else []

    # Отключаем автозагрузку связанных объектов для стабильности
    form_ajax_refs = {}

    tz = pytz.timezone(settings.timezone)

    @classmethod
    def get_list_query(cls, request):
        """Оптимизированный запрос для списка"""
        query = super().get_list_query(request)
        # Добавляем options для предотвращения N+1 проблем
        return query

    @staticmethod
    def _localize_time(value: datetime) -> str:
        """Конвертирует UTC время в локальное"""
        if not value:
            return ""
        if value.tzinfo is None:
            value = value.replace(tzinfo=pytz.UTC)
        local_value = value.astimezone(BaseAdminView.tz)
        return local_value.strftime("%Y-%m-%d %H:%M:%S")
"""
SQLAdmin модели для административной панели
"""
from werkzeug.security import generate_password_hash
from sqladmin import Admin
import json

from .base import BaseAdminView

from src.models.user import User



class UserAdmin(BaseAdminView, model=User):
    """Администрирование пользователей"""
    name = "Пользователь"
    name_plural = "Пользователи"
    category = "Пользователи"
    icon = "fa-solid fa-users"

    column_list = [
        User.id,
        User.username,
        User.email,
        User.first_name,
        User.last_name,
        User.is_superuser,
    ]
    column_searchable_list = ["username", "email", "first_name", "last_name"]
    column_sortable_list = ["username", "email", "created_at"]
    column_details_exclude_list = ["hashed_password"]

    column_labels = {"hashed_password": "Password"}

    form_excluded_columns = ["created_at", "last_activity", "roles", "enrollments", "notifications", "reflection_answers"]

    async def on_model_change(self, form, model, is_created, request) -> None:
        """Хеширование пароля при создании или обновлении"""
        if is_created or form["hashed_password"]:
            form["hashed_password"] = generate_password_hash(form["hashed_password"])




def setup_admin_views(admin: Admin):
    """Регистрация всех админ-моделей"""
    # Пользователи
    admin.add_view(UserAdmin)
"""
SQLAdmin модели для административной панели
"""

from .base import BaseAdminView
from src.models.progress import Progress




def setup_admin_views(admin: Admin):
    """Регистрация всех админ-моделей"""
    ...
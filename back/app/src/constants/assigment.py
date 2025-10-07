from enum import StrEnum

class AssignmentType(StrEnum):
    """Типы заданий"""
    PRACTICE = "practice"      # практическое задание
    TEST = "test"              # тест
    PROJECT = "project"        # проект
    ESSAY = "essay"            # эссе / работа с текстом
    OTHER = "other"            # другое
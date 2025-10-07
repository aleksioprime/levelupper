from typing import Generic, TypeVar, List

from fastapi import Query
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Универсальная структура ответа для постраничной навигации (pagination).
    Позволяет возвращать список элементов с информацией о текущей странице и наличии следующих/предыдущих страниц.
    """
    items: List[T] = Field(..., description="Список элементов на текущей странице")
    total: int = Field(..., description="Общее количество элементов")
    limit: int = Field(..., description="Максимальное количество элементов на странице")
    offset: int = Field(..., description="Смещение от начала коллекции")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_previous: bool = Field(..., description="Есть ли предыдущая страница")


class BasePaginationParams(BaseModel):
    """ Базовый класс параметров пагинации """
    limit: int = Field(Query(alias='limit', gt=0))
    offset: int = Field(Query(alias='offset', ge=0))
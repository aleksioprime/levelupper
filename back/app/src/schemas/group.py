from uuid import UUID
from pydantic import BaseModel, Field


class GroupSchema(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор группы")
    name: str = Field(..., description="Название группы")

    class Config:
        from_attributes = True


class GroupCreateSchema(BaseModel):
    name: str = Field(..., description="Название новой группы")


class GroupUpdateSchema(BaseModel):
    name: str | None = Field(None, description="Новое название группы")


class GroupDetailSchema(GroupSchema):
    ...  # Здесь можно добавить дополнительные поля для детальной информации о группе
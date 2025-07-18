from pydantic import BaseModel
from uuid import UUID

class Course(BaseModel):
    id: UUID
    title: str
    description: str
    teacher_id: UUID
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    title: str
    description: str
    completed: bool
    created_at: datetime
    owner_uuid: UUID

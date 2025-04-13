from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    description: str
    completed: bool | None = False


class TaskFromDB(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
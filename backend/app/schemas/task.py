from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: str = "medium"
    deadline: datetime | None = None
    estimated_minutes: int = Field(gt=0)
    category: str | None = None
    preferred_time: str | None = None


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    priority: str
    deadline: datetime | None
    estimated_minutes: int
    category: str | None
    status: str
    preferred_time: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None
    priority: str | None = None
    deadline: datetime | None = None
    estimated_minutes: int | None = Field(
        default=None,
        gt=0,
    )
    category: str | None = None
    preferred_time: str | None = None
    status: str | None = None
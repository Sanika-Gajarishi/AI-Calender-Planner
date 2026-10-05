from datetime import datetime

from pydantic import BaseModel, Field


class TaskUnderstandingRequest(BaseModel):
    text: str = Field(
        min_length=3,
        max_length=2000,
    )


class TaskUnderstandingResponse(BaseModel):
    title: str
    description: str | None = None

    priority: str

    estimated_minutes: int = Field(
        gt=0,
        le=24 * 60,
    )

    deadline: datetime | None = None

    preferred_time: str | None = None

    category: str | None = None
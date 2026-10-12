from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScheduleItemResponse(BaseModel):
    task_id: int
    block_id: int | None = None
    title: str
    start: datetime
    end: datetime
    priority: str

    model_config = ConfigDict(
        from_attributes=True
    )


class ScheduleResponse(BaseModel):
    items: list[ScheduleItemResponse]
    total_minutes: int
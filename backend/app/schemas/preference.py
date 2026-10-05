from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class PreferenceCreate(BaseModel):
    work_start_time: time = time(18, 0)
    work_end_time: time = time(22, 0)

    preferred_work_period: str = "evening"

    max_daily_hours: int = Field(
        default=4,
        gt=0,
        le=24,
    )

    break_duration: int = Field(
        default=15,
        ge=0,
        le=120,
    )

    preferred_task_length: int = Field(
        default=60,
        gt=0,
        le=480,
    )

    timezone: str = "Asia/Kolkata"


class PreferenceResponse(BaseModel):
    id: int
    user_id: int

    work_start_time: time
    work_end_time: time

    preferred_work_period: str

    max_daily_hours: int
    break_duration: int
    preferred_task_length: int

    timezone: str

    model_config = ConfigDict(from_attributes=True)
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SchedulingTask:
    id: int
    title: str
    priority: str
    estimated_minutes: int
    remaining_minutes: int
    deadline: datetime | None
    preferred_time: str | None = None
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimeSlot:
    start: datetime
    end: datetime

    @property
    def duration_minutes(self) -> int:
        return int(
            (self.end - self.start).total_seconds() / 60
        )


@dataclass
class ScheduledTask:
    task_id: int
    title: str
    start: datetime
    end: datetime
    priority: str
    block_number: int = 1

    @property
    def duration_minutes(self) -> int:
        return int(
            (self.end - self.start).total_seconds() / 60
        )


@dataclass
class ScheduleBreak:
    start: datetime
    end: datetime

    @property
    def total_minutes(self) -> int:
        return int(
            (self.end - self.start).total_seconds() / 60
        )


@dataclass
class UnscheduledTask:
    task_id: int
    title: str
    reason: str


@dataclass
class GeneratedSchedule:
    scheduled_tasks: list[ScheduledTask]
    breaks: list[ScheduleBreak]
    unscheduled_tasks: list[UnscheduledTask]

    def __len__(self) -> int:
        return len(self.scheduled_tasks)

    def __getitem__(self, index: int) -> ScheduledTask:
        return self.scheduled_tasks[index]

@dataclass
class CalendarEvent:
    title: str
    start: datetime
    end: datetime
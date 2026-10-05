from datetime import datetime, timedelta

from app.models.task import Task
from app.scheduler.allocator import allocate_tasks
from app.scheduler.models import ScheduledTask, TimeSlot
from app.scheduler.prioritizer import prioritize_tasks
from app.scheduler.slot_finder import find_free_slots


def generate_daily_schedule(
    tasks: list[Task],
    work_start: datetime,
    work_end: datetime,
    busy_slots: list[TimeSlot],
    break_duration: int = 15,
    max_daily_hours: int = 4,
) -> list[ScheduledTask]:

    free_slots = find_free_slots(
        work_start=work_start,
        work_end=work_end,
        busy_slots=busy_slots,
    )

    prioritized_tasks = prioritize_tasks(
        tasks=tasks,
        current_time=work_start,
    )

    max_daily_minutes = max_daily_hours * 60

    limited_slots: list[TimeSlot] = []

    remaining_minutes = max_daily_minutes

    for slot in free_slots:

        if remaining_minutes <= 0:
            break

        allowed_minutes = min(
            slot.duration_minutes,
            remaining_minutes,
        )

        limited_slots.append(
            TimeSlot(
                start=slot.start,
                end=slot.start
                + timedelta(minutes=allowed_minutes),
            )
        )

        remaining_minutes -= allowed_minutes

    return allocate_tasks(
        tasks=prioritized_tasks,
        free_slots=limited_slots,
        break_duration=break_duration,
    )
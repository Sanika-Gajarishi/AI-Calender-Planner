from datetime import timedelta

from app.models.task import Task
from app.scheduler.models import (
    GeneratedSchedule,
    ScheduleBreak,
    ScheduledTask,
    TimeSlot,
    UnscheduledTask,
)


def allocate_tasks(
    tasks: list[Task],
    working_windows: list[TimeSlot],
    preferred_task_length: int,
    break_duration: int,
    max_daily_hours: int,
) -> GeneratedSchedule:

    scheduled_tasks: list[ScheduledTask] = []
    breaks: list[ScheduleBreak] = []
    unscheduled_tasks: list[UnscheduledTask] = []

    daily_work_minutes: dict = {}

    for task in tasks:

        remaining_minutes = task.estimated_minutes

        while remaining_minutes > 0:

            allocated = False

            for window in working_windows:

                current_time = window.start

                while current_time < window.end:

                    day = current_time.date()

                    used_minutes = daily_work_minutes.get(
                        day,
                        0,
                    )

                    max_minutes = max_daily_hours * 60

                    if used_minutes >= max_minutes:
                        break

                    available_minutes = int(
                        (
                            window.end - current_time
                        ).total_seconds() / 60
                    )

                    remaining_daily_minutes = (
                        max_minutes - used_minutes
                    )

                    if available_minutes <= 0:
                        break

                    allocation_minutes = min(
                        remaining_minutes,
                        preferred_task_length,
                        available_minutes,
                        remaining_daily_minutes,
                    )

                    if allocation_minutes <= 0:
                        break

                    task_end = (
                        current_time
                        + timedelta(
                            minutes=allocation_minutes
                        )
                    )

                    if task.deadline is not None:
                        deadline = task.deadline

                        if deadline.tzinfo is None:
                            deadline = deadline.replace(
                                tzinfo=current_time.tzinfo
                            )

                        if task_end > deadline:
                            break

                    scheduled_tasks.append(
                        ScheduledTask(
                            task_id=task.id,
                            title=task.title,
                            start=current_time,
                            end=task_end,
                            priority=task.priority,
                        )
                    )

                    daily_work_minutes[day] = (
                        used_minutes
                        + allocation_minutes
                    )

                    remaining_minutes -= (
                        allocation_minutes
                    )

                    current_time = task_end

                    allocated = True

                    if remaining_minutes <= 0:
                        break

                    if (
                        break_duration > 0
                        and current_time < window.end
                    ):
                        break_start = current_time

                        break_end = (
                            current_time
                            + timedelta(
                                minutes=break_duration
                            )
                        )

                        if break_end <= window.end:
                            breaks.append(
                                ScheduleBreak(
                                    start=break_start,
                                    end=break_end,
                                )
                            )

                            current_time = break_end

                if remaining_minutes <= 0:
                    break

            if not allocated:
                break

            if remaining_minutes <= 0:
                break

        if remaining_minutes > 0:
            unscheduled_tasks.append(
                UnscheduledTask(
                    task_id=task.id,
                    title=task.title,
                    reason=(
                        "Not enough available time "
                        "before the scheduling limit."
                    ),
                )
            )

    return GeneratedSchedule(
        scheduled_tasks=scheduled_tasks,
        breaks=breaks,
        unscheduled_tasks=unscheduled_tasks,
    )
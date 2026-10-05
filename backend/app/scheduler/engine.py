from datetime import date, time
from types import SimpleNamespace

from app.models.task import Task
from app.models.preference import UserPreference
from app.scheduler.allocator import allocate_tasks
from app.scheduler.models import GeneratedSchedule
from app.scheduler.prioritizer import prioritize_tasks
from app.scheduler.slot_finder import generate_working_windows


class SchedulingEngine:

    def generate_schedule(
        self,
        tasks: list[Task],
        start_date: date,
        end_date: date,
        preferences: UserPreference | None = None,
        work_start_hour: int | None = None,
        work_end_hour: int | None = None,
        slot_minutes: int | None = None,
    ) -> GeneratedSchedule:

        if preferences is None:
            if work_start_hour is None or work_end_hour is None:
                raise ValueError(
                    "preferences or working hours are required"
                )

            preferences = SimpleNamespace(
                work_start_time=time(work_start_hour),
                work_end_time=time(work_end_hour),
                preferred_task_length=slot_minutes or 60,
                break_duration=0,
                max_daily_hours=work_end_hour - work_start_hour,
            )

        prioritized_tasks = prioritize_tasks(tasks)

        working_windows = generate_working_windows(
            start_date=start_date,
            end_date=end_date,
            work_start_time=preferences.work_start_time,
            work_end_time=preferences.work_end_time,
        )

        schedule = allocate_tasks(
            tasks=prioritized_tasks,
            working_windows=working_windows,
            preferred_task_length=(
                preferences.preferred_task_length
            ),
            break_duration=preferences.break_duration,
            max_daily_hours=preferences.max_daily_hours,
        )

        return schedule
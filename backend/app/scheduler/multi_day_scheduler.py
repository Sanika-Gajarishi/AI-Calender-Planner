from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, tzinfo

from app.scheduler.task_input import SchedulingTask
from app.scheduler.models import ScheduledTask, TimeSlot
from app.scheduler.slot_finder import find_free_slots
from app.scheduler.prioritizer import prioritize_tasks


@dataclass
class DailyAvailability:
    date: date
    work_start: time
    work_end: time
    busy_slots: list[TimeSlot]
    timezone: tzinfo | None = None


PREFERRED_TIME_WINDOWS = {
    "morning": (
        time(6, 0),
        time(12, 0),
    ),
    "afternoon": (
        time(12, 0),
        time(17, 0),
    ),
    "evening": (
        time(17, 0),
        time(22, 0),
    ),
}


def filter_slots_by_preferred_time(
    slots: list[TimeSlot],
    preferred_time: str | None,
) -> list[TimeSlot]:

    if not preferred_time:
        return slots

    preferred_time = preferred_time.lower().strip()

    if preferred_time in {
        "anytime",
        "any",
        "flexible",
    }:
        return slots

    if preferred_time not in PREFERRED_TIME_WINDOWS:
        return slots

    preferred_start, preferred_end = (
        PREFERRED_TIME_WINDOWS[preferred_time]
    )

    filtered_slots: list[TimeSlot] = []

    for slot in slots:

        slot_start = slot.start
        slot_end = slot.end

        preferred_start_datetime = datetime.combine(
            slot_start.date(),
            preferred_start,
            tzinfo=slot_start.tzinfo,
        )

        preferred_end_datetime = datetime.combine(
            slot_start.date(),
            preferred_end,
            tzinfo=slot_start.tzinfo,
        )

        effective_start = max(
            slot_start,
            preferred_start_datetime,
        )

        effective_end = min(
            slot_end,
            preferred_end_datetime,
        )

        if effective_start < effective_end:
            filtered_slots.append(
                TimeSlot(
                    start=effective_start,
                    end=effective_end,
                )
            )

    return filtered_slots


def generate_multi_day_schedule(
    tasks: list[SchedulingTask],
    days: list[DailyAvailability],
    max_daily_hours: int = 4,
    break_duration: int = 15,
) -> list[ScheduledTask]:

    print("\n========== MULTI DAY SCHEDULER ==========")
    print("Tasks received:", len(tasks))
    for task in tasks:
        print(
            f"Task {task.id}: "
            f"{task.title}, "
            f"remaining={getattr(task, 'remaining_minutes', task.estimated_minutes)}, "
            f"deadline={task.deadline}"
        )
    print("Days received:", len(days))

    schedule: list[ScheduledTask] = []

    block_numbers: dict[int, int] = {}

    remaining_minutes = {
        task.id: getattr(
            task,
            "remaining_minutes",
            task.estimated_minutes,
        )
        for task in tasks
    }

    max_daily_minutes = max_daily_hours * 60

    prioritized_tasks = prioritize_tasks(tasks)

    for day in days:

        if not any(
            minutes > 0
            for minutes in remaining_minutes.values()
        ):
            break

        work_start = datetime.combine(
            day.date,
            day.work_start,
            tzinfo=day.timezone,
        )

        work_end = datetime.combine(
            day.date,
            day.work_end,
            tzinfo=day.timezone,
        )

        free_slots = find_free_slots(
            work_start=work_start,
            work_end=work_end,
            busy_slots=day.busy_slots,
        )

        print(
            f"\nDAY {day.date}: "
            f"work={work_start} -> {work_end}"
        )
        print("Busy slots:", day.busy_slots)
        print("Free slots:", free_slots)
        for free_slot in free_slots:
            print(
                "  FREE:",
                free_slot.start,
                "->",
                free_slot.end,
                f"({free_slot.duration_minutes} min)",
            )

        daily_remaining = max_daily_minutes

        for task in prioritized_tasks:

            if daily_remaining <= 0:
                break

            task_remaining = remaining_minutes[
                task.id
            ]

            if task_remaining <= 0:
                continue

            task_slots = filter_slots_by_preferred_time(
                slots=free_slots,
                preferred_time=getattr(
                    task,
                    "preferred_time",
                    None,
                ),
            )

            for slot in task_slots:

                if daily_remaining <= 0:
                    break

                if task_remaining <= 0:
                    break

                deadline_minutes = (
                    get_available_minutes_before_deadline(
                        slot=slot,
                        deadline=task.deadline,
                    )
                )

                available_minutes = min(
                    deadline_minutes,
                    daily_remaining,
                    task_remaining,
                    slot.duration_minutes,
                )

                if available_minutes <= 0:
                    continue

                start = slot.start

                end = start + timedelta(
                    minutes=available_minutes
                )

                block_numbers.setdefault(
                    task.id,
                    0,
                )

                block_numbers[task.id] += 1

                schedule.append(
                    ScheduledTask(
                        task_id=task.id,
                        title=task.title,
                        start=start,
                        end=end,
                        priority=task.priority,
                        block_number=block_numbers[
                            task.id
                        ],
                    )
                )

                remaining_minutes[task.id] -= (
                    available_minutes
                )

                task_remaining -= available_minutes

                daily_remaining -= available_minutes

                free_slots = update_free_slots(
                    free_slots,
                    slot,
                    end,
                )

    print("\nFINAL GENERATED SCHEDULE:")
    for item in schedule:
        print(
            item.task_id,
            item.title,
            item.start,
            "->",
            item.end,
        )
    print("Total blocks:", len(schedule))
    print("========================================\n")

    return schedule


def update_free_slots(
    free_slots: list[TimeSlot],
    used_slot: TimeSlot,
    new_start: datetime,
) -> list[TimeSlot]:

    updated_slots: list[TimeSlot] = []

    for slot in free_slots:

        if slot.start == used_slot.start and (
            slot.end == used_slot.end
        ):

            if new_start < slot.end:
                updated_slots.append(
                    TimeSlot(
                        start=new_start,
                        end=slot.end,
                    )
                )

        else:
            updated_slots.append(slot)

    return updated_slots


def get_available_minutes_before_deadline(
    slot: TimeSlot,
    deadline: datetime | None,
) -> int:

    if deadline is None:
        return slot.duration_minutes

    if (
        slot.start.tzinfo is not None
        and deadline.tzinfo is None
    ):
        deadline = deadline.replace(
            tzinfo=slot.start.tzinfo
        )

    # Treat midnight deadlines as the end of that calendar day.
    if deadline.time() == time(0, 0):
        deadline = datetime.combine(
            deadline.date(),
            time(23, 59, 59),
            tzinfo=deadline.tzinfo,
        )

    if slot.start >= deadline:
        return 0

    effective_end = min(
        slot.end,
        deadline,
    )

    return max(
        0,
        int(
            (
                effective_end - slot.start
            ).total_seconds()
            / 60
        ),
    )
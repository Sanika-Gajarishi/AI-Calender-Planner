from datetime import date, datetime, time, timedelta

from app.scheduler.models import TimeSlot


def generate_working_windows(
    start_date: date,
    end_date: date,
    work_start_time: time,
    work_end_time: time,
) -> list[TimeSlot]:
    """
    Generate one continuous working window for each day.
    """

    windows: list[TimeSlot] = []

    current_date = start_date

    while current_date <= end_date:
        start_datetime = datetime.combine(
            current_date,
            work_start_time,
        )

        end_datetime = datetime.combine(
            current_date,
            work_end_time,
        )

        if end_datetime > start_datetime:
            windows.append(
                TimeSlot(
                    start=start_datetime,
                    end=end_datetime,
                )
            )

        current_date += timedelta(days=1)

    return windows


def generate_working_slots(
    start_date: datetime,
    end_date: datetime,
    work_start_hour: int,
    work_end_hour: int,
    slot_minutes: int,
) -> list[TimeSlot]:
    """Generate fixed-length working slots for each requested day."""

    slots: list[TimeSlot] = []
    current_date = start_date.date()
    final_date = end_date.date()

    while current_date <= final_date:
        current_time = datetime.combine(
            current_date,
            time(hour=work_start_hour),
        )
        day_end = datetime.combine(
            current_date,
            time(hour=work_end_hour),
        )

        while current_time < day_end:
            slot_end = current_time + timedelta(minutes=slot_minutes)

            if slot_end > day_end:
                break

            slots.append(
                TimeSlot(
                    start=current_time,
                    end=slot_end,
                )
            )
            current_time = slot_end

        current_date += timedelta(days=1)

    return slots


def find_free_slots(
    work_start: datetime,
    work_end: datetime,
    busy_slots: list[TimeSlot],
) -> list[TimeSlot]:
    """Return the portions of a working period not covered by busy slots."""

    free_slots: list[TimeSlot] = []
    current_time = work_start

    for busy_slot in sorted(busy_slots, key=lambda slot: slot.start):
        busy_start_time = busy_slot.start
        busy_end_time = busy_slot.end

        if work_start.tzinfo is not None:
            if busy_start_time.tzinfo is not None:
                busy_start_time = busy_start_time.astimezone(work_start.tzinfo)
            if busy_end_time.tzinfo is not None:
                busy_end_time = busy_end_time.astimezone(work_start.tzinfo)

        busy_start = max(busy_start_time, work_start)
        busy_end = min(busy_end_time, work_end)

        if busy_end <= work_start or busy_start >= work_end:
            continue

        if current_time < busy_start:
            free_slots.append(
                TimeSlot(
                    start=current_time,
                    end=busy_start,
                )
            )

        current_time = max(current_time, busy_end)

        if current_time >= work_end:
            break

    if current_time < work_end:
        free_slots.append(
            TimeSlot(
                start=current_time,
                end=work_end,
            )
        )

    return free_slots
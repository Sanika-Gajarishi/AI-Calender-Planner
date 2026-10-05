from dataclasses import replace
from datetime import timedelta

from app.scheduler.models import ScheduledTask


def add_breaks(
    schedule: list[ScheduledTask],
    break_duration: int,
) -> list[ScheduledTask]:

    if not schedule:
        return []

    updated_schedule = [schedule[0]]

    for item in schedule[1:]:

        previous = updated_schedule[-1]

        gap_minutes = (
            item.start - previous.end
        ).total_seconds() / 60

        if gap_minutes < break_duration:

            new_start = (
                previous.end
                + timedelta(minutes=break_duration)
            )

            item = replace(
                item,
                start=new_start,
                end=(
                    new_start
                    + timedelta(
                        minutes=item.duration_minutes
                    )
                ),
            )

        updated_schedule.append(item)

    return updated_schedule
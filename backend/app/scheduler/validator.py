from app.scheduler.models import ScheduledTask


def validate_schedule(
    schedule: list[ScheduledTask],
) -> bool:

    if not schedule:
        return True

    ordered = sorted(
        schedule,
        key=lambda item: item.start,
    )

    for index in range(1, len(ordered)):

        previous = ordered[index - 1]
        current = ordered[index]

        if current.start < previous.end:
            return False

    return True
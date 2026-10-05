from datetime import datetime

from app.core.timezone import IST
from app.scheduler.task_input import SchedulingTask


PRIORITY_WEIGHT = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


def calculate_task_score(
    task: SchedulingTask,
) -> float:

    score = PRIORITY_WEIGHT.get(
        task.priority.lower(),
        1,
    )

    if task.deadline is not None:

        now = datetime.now(IST)

        deadline = task.deadline

        if deadline.tzinfo is None:
            deadline = deadline.replace(
                tzinfo=IST
            )

        hours_remaining = (
            deadline - now
        ).total_seconds() / 3600

        if hours_remaining <= 24:
            score += 5

        elif hours_remaining <= 72:
            score += 3

        elif hours_remaining <= 168:
            score += 1

    return score


def prioritize_tasks(
    tasks: list[SchedulingTask],
) -> list[SchedulingTask]:

    return sorted(
        tasks,
        key=calculate_task_score,
        reverse=True,
    )
from app.models.task import Task
from app.scheduler.task_input import SchedulingTask
from app.services.task_progress import get_remaining_minutes


def task_to_scheduling_task(
    task: Task,
    use_remaining: bool = True,
) -> SchedulingTask:

    if use_remaining:
        remaining_minutes = get_remaining_minutes(task)
    else:
        remaining_minutes = task.estimated_minutes

    return SchedulingTask(
        id=task.id,
        title=task.title,
        priority=task.priority,
        estimated_minutes=task.estimated_minutes,
        remaining_minutes=remaining_minutes,
        deadline=task.deadline,
        preferred_time=task.preferred_time,
    )
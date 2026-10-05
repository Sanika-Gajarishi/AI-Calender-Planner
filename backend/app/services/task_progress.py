def get_scheduled_minutes(task) -> int:

    return sum(
        block.duration_minutes
        for block in task.scheduled_blocks
    )


def get_remaining_minutes(task) -> int:

    scheduled_minutes = get_scheduled_minutes(
        task
    )

    return max(
        0,
        task.estimated_minutes - scheduled_minutes,
    )
from app.models.scheduled_block import ScheduledBlock


def save_schedule_blocks(
    db,
    schedule,
):

    blocks = []

    for item in schedule:

        block = ScheduledBlock(
            task_id=item.task_id,
            start_time=item.start,
            end_time=item.end,
            duration_minutes=item.duration_minutes,
        )

        db.add(block)

        blocks.append(block)

    db.commit()

    return blocks
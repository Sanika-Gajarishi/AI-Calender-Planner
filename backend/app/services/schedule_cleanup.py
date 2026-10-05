from sqlalchemy import delete

from app.models.scheduled_block import ScheduledBlock


def delete_future_blocks(
    db,
    start_time,
):

    statement = delete(
        ScheduledBlock
    ).where(
        ScheduledBlock.start_time >= start_time
    )

    db.execute(statement)

    db.commit()
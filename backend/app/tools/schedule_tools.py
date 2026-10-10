from datetime import date

from langchain.tools import tool
from sqlalchemy.orm import Session

from app.services.schedule_service import (
    ScheduleService,
)


def generate_schedule_data(
    db: Session,
    user_id: int,
    start_date: date,
    number_of_days: int = 7,
):

    service = ScheduleService(db)

    schedule = service.generate_schedule(
        user_id=user_id,
        start_date=start_date,
        number_of_days=number_of_days,
    )

    return [
        {
            "task_id": item.task_id,
            "title": item.title,
            "start": item.start.isoformat(),
            "end": item.end.isoformat(),
            "priority": item.priority,
        }
        for item in schedule
    ]


def create_schedule_tools(
    db: Session,
    user_id: int,
):

    @tool
    def generate_my_schedule(
        start_date: str,
        number_of_days: int = 7,
    ) -> list[dict]:
        """
        Generate an optimized schedule for the current user.

        start_date must be in YYYY-MM-DD format.
        """

        parsed_date = date.fromisoformat(
            start_date
        )

        return generate_schedule_data(
            db=db,
            user_id=user_id,
            start_date=parsed_date,
            number_of_days=number_of_days,
        )

    return [
        generate_my_schedule,
    ]
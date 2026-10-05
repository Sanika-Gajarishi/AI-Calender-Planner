from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.schedule import ScheduleResponse
from app.services.schedule_service import ScheduleService

from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/schedule",
    tags=["Schedule"],
)


@router.get(
    "",
    response_model=ScheduleResponse,
)
def get_schedule(
    start_date: date,
    number_of_days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ScheduleService(db)
    try:
        schedule = service.get_saved_schedule(
            user_id=current_user.id,
            start_date=start_date,
            number_of_days=number_of_days,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )
    total_minutes = sum(
        item.duration_minutes
        for item in schedule
    )
    return ScheduleResponse(
        items=schedule,
        total_minutes=total_minutes,
    )


@router.post(
    "/generate",
    response_model=ScheduleResponse,
)
def generate_schedule(
    start_date: date,
    number_of_days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    service = ScheduleService(db)

    try:

        schedule = service.generate_schedule(
            user_id=current_user.id,
            start_date=start_date,
            number_of_days=number_of_days,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    total_minutes = sum(
        item.duration_minutes
        for item in schedule
    )

    return ScheduleResponse(
        items=schedule,
        total_minutes=total_minutes,
    )


@router.post(
    "/sync-google",
)
def sync_schedule_to_google(
    start_date: date,
    number_of_days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    service = ScheduleService(db)
    try:
        result = (
            service.sync_schedule_to_google_calendar(
                user_id=current_user.id,
                start_date=start_date,
                number_of_days=number_of_days,
            )
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )
    return {
        "success": True,
        "message": (
            "Schedule synced to Google Calendar"
        ),
        "events_created": result["created"],
        "events_skipped": result["skipped"],
    }
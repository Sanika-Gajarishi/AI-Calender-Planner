from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User

from app.integrations.google_auth import get_google_credentials
from app.integrations.google_calendar import GoogleCalendarService


router = APIRouter(
    prefix="/calendar",
    tags=["Google Calendar"],
)


@router.get("/status")
def calendar_status(
    current_user: User = Depends(get_current_user),
):
    if current_user.google_id == "connected":
        return {
            "connected": True,
            "message": "Google Calendar connected",
        }

    return {
        "connected": False,
        "message": "Google Calendar not connected",
    }


@router.post("/connect")
def connect_google_calendar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        credentials = get_google_credentials()

        if not credentials:
            raise HTTPException(
                status_code=400,
                detail="Google Calendar authorization failed.",
            )

        current_user.google_id = "connected"

        db.commit()
        db.refresh(current_user)

        return {
            "connected": True,
            "message": "Google Calendar connected successfully.",
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Google Calendar connection failed: {error}",
        )


@router.get("/events")
def get_calendar_events(
    days: int = 7,
    current_user: User = Depends(get_current_user),
):
    if current_user.google_id != "connected":
        raise HTTPException(
            status_code=400,
            detail="Google Calendar is not connected.",
        )

    try:
        credentials = get_google_credentials()

        service = GoogleCalendarService(
            credentials=credentials
        )

        start_time = datetime.now(timezone.utc)

        end_time = start_time + timedelta(
            days=days
        )

        events = service.get_events(
            start_time=start_time,
            end_time=end_time,
        )

        return {
            "events": events,
            "count": len(events),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Google Calendar events: {error}",
        )
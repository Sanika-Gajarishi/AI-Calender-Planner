from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.preference import UserPreference
from app.models.user import User
from app.schemas.preference import (
    PreferenceCreate,
    PreferenceResponse,
)


router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"],
)


@router.post(
    "/",
    response_model=PreferenceResponse,
)
def create_preferences(
    preference_data: PreferenceCreate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == 1)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    existing_preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user.id)
        .first()
    )

    if existing_preferences:
        raise HTTPException(
            status_code=400,
            detail="Preferences already exist for this user",
        )

    preferences = UserPreference(
        user_id=user.id,
        work_start_time=preference_data.work_start_time,
        work_end_time=preference_data.work_end_time,
        preferred_work_period=(
            preference_data.preferred_work_period
        ),
        max_daily_hours=(
            preference_data.max_daily_hours
        ),
        break_duration=(
            preference_data.break_duration
        ),
        preferred_task_length=(
            preference_data.preferred_task_length
        ),
        timezone=preference_data.timezone,
    )

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences

@router.get(
    "/",
    response_model=PreferenceResponse,
)
def get_preferences(
    db: Session = Depends(get_db),
):
    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == 1)
        .first()
    )

    if preferences is None:
        raise HTTPException(
            status_code=404,
            detail="Preferences not found",
        )

    return preferences
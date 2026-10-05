from datetime import time

from sqlalchemy import ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    work_start_time: Mapped[time] = mapped_column(
        Time,
        default=time(18, 0),
        nullable=False,
    )

    work_end_time: Mapped[time] = mapped_column(
        Time,
        default=time(22, 0),
        nullable=False,
    )

    preferred_work_period: Mapped[str] = mapped_column(
        String(30),
        default="evening",
        nullable=False,
    )

    max_daily_hours: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
    )

    break_duration: Mapped[int] = mapped_column(
        Integer,
        default=15,
        nullable=False,
    )

    preferred_task_length: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        default="Asia/Kolkata",
        nullable=False,
    )
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.integrations.google_auth import get_google_credentials
from app.integrations.google_calendar import GoogleCalendarService

from app.models.preference import UserPreference
from app.models.task import Task
from app.models.scheduled_block import ScheduledBlock

from app.scheduler.multi_day_scheduler import (
    DailyAvailability,
    generate_multi_day_schedule,
)
from app.scheduler.models import ScheduledTask

from app.services.calendar_service import CalendarService
from app.services.task_mapper import task_to_scheduling_task


class ScheduleService:

    def __init__(self, db: Session):
        self.db = db

        credentials = get_google_credentials()

        google_calendar = GoogleCalendarService(
            credentials
        )

        self.calendar_service = CalendarService(
            google_calendar
        )

    def get_saved_schedule(
        self,
        user_id: int,
        start_date: date,
        number_of_days: int = 7,
    ) -> list[ScheduledTask]:
        preferences = (
            self.db.query(UserPreference)
            .filter(
                UserPreference.user_id == user_id
            )
            .first()
        )

        if preferences is None:
            raise ValueError(
                "User preferences not found."
            )

        timezone = ZoneInfo(
            preferences.timezone
        )
        range_start = datetime.combine(
            start_date,
            preferences.work_start_time,
            tzinfo=timezone,
        )
        range_end = datetime.combine(
            start_date + timedelta(days=number_of_days),
            preferences.work_end_time,
            tzinfo=timezone,
        )

        blocks = (
            self.db.query(ScheduledBlock)
            .join(Task)
            .filter(
                Task.user_id == user_id,
                ScheduledBlock.start_time >= range_start,
                ScheduledBlock.end_time <= range_end,
            )
            .order_by(ScheduledBlock.start_time)
            .all()
        )

        return [
            ScheduledTask(
                task_id=block.task_id,
                title=block.task.title,
                start=block.start_time,
                end=block.end_time,
                priority=block.task.priority,
            )
            for block in blocks
        ]

    def generate_schedule(
        self,
        user_id: int,
        start_date: date,
        number_of_days: int = 7,
    ):
        # --------------------------------------------------
        # 1. Get user preferences
        # --------------------------------------------------

        preferences = (
            self.db.query(UserPreference)
            .filter(
                UserPreference.user_id == user_id
            )
            .first()
        )

        if preferences is None:
            raise ValueError(
                "User preferences not found."
            )

        timezone = ZoneInfo(
            preferences.timezone
        )

        # --------------------------------------------------
        # 2. Define schedule date range
        # --------------------------------------------------

        range_start = datetime.combine(
            start_date,
            preferences.work_start_time,
            tzinfo=timezone,
        )

        range_end = datetime.combine(
            start_date
            + timedelta(days=number_of_days),
            preferences.work_end_time,
            tzinfo=timezone,
        )

        # --------------------------------------------------
        # 3. Remove previously generated blocks
        #    BEFORE calculating remaining task time
        # --------------------------------------------------

        existing_blocks = (
            self.db.query(ScheduledBlock)
            .join(Task)
            .filter(
                Task.user_id == user_id,
                ScheduledBlock.start_time >= range_start,
                ScheduledBlock.end_time <= range_end,
            )
            .all()
        )

        # Delete previously generated Google Calendar events
        # before deleting their database records.
        for block in existing_blocks:
            if block.google_event_id:
                try:
                    self.calendar_service.google_calendar.delete_event(
                        block.google_event_id
                    )
                except Exception as error:
                    print(
                        f"Could not delete Google event "
                        f"{block.google_event_id}: {error}"
                    )
            self.db.delete(block)

        self.db.flush()

        # --------------------------------------------------
        # 4. Get user's pending tasks
        # --------------------------------------------------

        tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.status != "completed",
            )
            .all()
        )

        tasks_with_remaining_time = []

        print("\n========== SCHEDULE DEBUG ==========")
        print("Total tasks:", len(tasks))
        for task in tasks:
            scheduling_task = task_to_scheduling_task(
                task
            )

            print(
                f"TASK {task.id}: "
                f"title={task.title!r}, "
                f"estimated={task.estimated_minutes}, "
                f"remaining={scheduling_task.remaining_minutes}, "
                f"deadline={task.deadline}, "
                f"priority={task.priority}"
            )

            if scheduling_task.remaining_minutes > 0:
                tasks_with_remaining_time.append(
                    scheduling_task
                )

        print(
            "Tasks sent to scheduler:",
            len(tasks_with_remaining_time),
        )
        print(
            "Tasks:",
            tasks_with_remaining_time,
        )

        # --------------------------------------------------
        # 5. Build daily availability
        # --------------------------------------------------

        days = []

        for day_offset in range(number_of_days):

            current_date = (
                start_date
                + timedelta(days=day_offset)
            )

            work_start = datetime.combine(
                current_date,
                preferences.work_start_time,
                tzinfo=timezone,
            )

            work_end = datetime.combine(
                current_date,
                preferences.work_end_time,
                tzinfo=timezone,
            )

            busy_slots = (
                self.calendar_service.get_busy_slots(
                    start=work_start,
                    end=work_end,
                )
            )

            print(
                     f"\nBUSY SLOTS FOR {current_date}:"
            )

            for slot in busy_slots:
                 print(
                         f"  BUSY: {slot.start} -> {slot.end}"
          )

            days.append(
                DailyAvailability(
                    date=current_date,
                    work_start=preferences.work_start_time,
                    work_end=preferences.work_end_time,
                    busy_slots=busy_slots,
                    timezone=timezone,
                )
            )

        # --------------------------------------------------
        # 6. Generate schedule
        # --------------------------------------------------

        generated_schedule = generate_multi_day_schedule(
            tasks=tasks_with_remaining_time,
            days=days,
            max_daily_hours=preferences.max_daily_hours,
            break_duration=preferences.break_duration,
        )

        # --------------------------------------------------
        # 7. Save generated schedule
        # --------------------------------------------------

        for scheduled_task in generated_schedule:

            block = ScheduledBlock(
                task_id=scheduled_task.task_id,
                start_time=scheduled_task.start,
                end_time=scheduled_task.end,
                duration_minutes=scheduled_task.duration_minutes,
            )

            self.db.add(block)

        self.db.commit()

        # --------------------------------------------------
        # 8. Return generated schedule
        # --------------------------------------------------

        return generated_schedule

    def sync_schedule_to_google_calendar(
        self,
        user_id: int,
        start_date: date,
        number_of_days: int = 7,
    ):
        preferences = (
            self.db.query(UserPreference)
            .filter(
                UserPreference.user_id == user_id
            )
            .first()
        )

        if preferences is None:
            raise ValueError(
                "User preferences not found."
            )

        timezone = ZoneInfo(
            preferences.timezone
        )

        range_start = datetime.combine(
            start_date,
            preferences.work_start_time,
            tzinfo=timezone,
        )

        range_end = datetime.combine(
            start_date + timedelta(days=number_of_days),
            preferences.work_end_time,
            tzinfo=timezone,
        )

        blocks = (
            self.db.query(ScheduledBlock)
            .join(Task)
            .filter(
                Task.user_id == user_id,
                ScheduledBlock.start_time >= range_start,
                ScheduledBlock.end_time <= range_end,
            )
            .order_by(
                ScheduledBlock.start_time
            )
            .all()
        )

        created_count = 0
        skipped_count = 0

        for block in blocks:
            if block.google_event_id:
                skipped_count += 1
                continue

            task = (
                self.db.query(Task)
                .filter(
                    Task.id == block.task_id
                )
                .first()
            )

            if task is None:
                continue

            event = (
                self.calendar_service.google_calendar
                .create_scheduled_task_event(
                    title=task.title,
                    start_time=block.start_time,
                    end_time=block.end_time,
                    description=(
                        "Created by AI Calendar Planner\n"
                        f"Task ID: {task.id}"
                    ),
                )
            )

            block.google_event_id = event.get("id")
            created_count += 1

        self.db.commit()

        return {
            "created": created_count,
            "skipped": skipped_count,
        }
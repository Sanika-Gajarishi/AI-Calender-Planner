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
            start_date
            + timedelta(days=number_of_days),
            preferences.work_end_time,
            tzinfo=timezone,
        )

        

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
                task,
                use_remaining=True,
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

        

        generated_schedule = generate_multi_day_schedule(
            tasks=tasks_with_remaining_time,
            days=days,
            max_daily_hours=preferences.max_daily_hours,
            break_duration=preferences.break_duration,
        )

        

        for scheduled_task in generated_schedule:

            block = ScheduledBlock(
                task_id=scheduled_task.task_id,
                start_time=scheduled_task.start,
                end_time=scheduled_task.end,
                duration_minutes=scheduled_task.duration_minutes,
            )

            self.db.add(block)

        self.db.commit()

        

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

    def reschedule_task(
        self,
        user_id: int,
        task_id: int,
        new_start: datetime,
        new_end: datetime,
    ):
        

        task = (
            self.db.query(Task)
            .filter(
                Task.id == task_id,
                Task.user_id == user_id,
            )
            .first()
        )

        if task is None:
            raise ValueError("Task not found.")

        

        block = (
            self.db.query(ScheduledBlock)
            .join(Task)
            .filter(
                ScheduledBlock.task_id == task_id,
                Task.user_id == user_id,
            )
            .order_by(ScheduledBlock.start_time)
            .first()
        )

        if block is None:
            raise ValueError(
                "No scheduled block found for this task."
            )

        

        if new_end <= new_start:
            raise ValueError(
                "End time must be after start time."
            )

        duration_minutes = int(
            (new_end - new_start).total_seconds() / 60
        )

        if duration_minutes <= 0:
            raise ValueError(
                "Duration must be greater than zero."
            )

        

        calendar_events = self.calendar_service.google_calendar.get_events(
            start_time=new_start,
            end_time=new_end,
        )

        conflicts = []

        for event in calendar_events:

            event_id = event.get("id")

            # Ignore the Google Calendar event belonging to
            # the task that we are currently rescheduling.
            if (
                block.google_event_id
                and event_id == block.google_event_id
            ):
                continue

            event_start = event.get(
                "start",
                {},
            ).get("dateTime")

            event_end = event.get(
                "end",
                {},
            ).get("dateTime")

            if not event_start or not event_end:
                continue

            try:
                existing_start = datetime.fromisoformat(
                    event_start.replace("Z", "+00:00")
                )

                existing_end = datetime.fromisoformat(
                    event_end.replace("Z", "+00:00")
                )

            except ValueError:
                continue

            # Standard interval overlap check.
            if (
                new_start < existing_end
                and new_end > existing_start
            ):
                conflicts.append(
                    {
                        "title": event.get(
                            "summary",
                            "Untitled event",
                        ),
                        "start": existing_start.isoformat(),
                        "end": existing_end.isoformat(),
                    }
                )

        

        if conflicts:

            conflict_lines = []

            for conflict in conflicts:
                conflict_lines.append(
                    f"- {conflict['title']}: "
                    f"{conflict['start']} -> "
                    f"{conflict['end']}"
                )

            raise ValueError(
                "The new time conflicts with existing "
                "Google Calendar events:\n"
                + "\n".join(conflict_lines)
            )

        

        if block.google_event_id:

            self.calendar_service.google_calendar.update_event(
                event_id=block.google_event_id,
                title=task.title,
                start_time=new_start,
                end_time=new_end,
                description=(
                    "Created by AI Calendar Planner\n"
                    f"Task ID: {task.id}"
                ),
            )

        
        block.start_time = new_start
        block.end_time = new_end
        block.duration_minutes = duration_minutes

        self.db.commit()
        self.db.refresh(block)


        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "start": block.start_time.isoformat(),
            "end": block.end_time.isoformat(),
            "duration_minutes": block.duration_minutes,
            "google_event_id": block.google_event_id,
        }
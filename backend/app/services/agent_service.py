from datetime import date, datetime, timedelta, timezone
import re
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.agents.calendar_agent import CalendarAgent
from app.agents.tools import create_calendar_tools
from app.models.scheduled_block import ScheduledBlock
from app.models.task import Task
from app.services.schedule_service import ScheduleService

from app.integrations.google_auth import get_google_credentials
from app.integrations.google_calendar import GoogleCalendarService


class AgentService:

    def __init__(
        self,
        db: Session,
        user_id: int,
    ):
        self.db = db
        self.user_id = user_id
        self._user_timezone = "Asia/Kolkata"  # Default timezone

    def get_tasks(self):
        tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == self.user_id,
                Task.status == "pending",
            )
            .order_by(Task.created_at.desc())
            .all()
        )

        return [
            {
                "id": task.id,
                "title": task.title,
                "priority": task.priority,
                "estimated_minutes": task.estimated_minutes,
                "deadline": (
                    task.deadline.isoformat()
                    if task.deadline
                    else None
                ),
                "category": task.category,
                "preferred_time": task.preferred_time,
            }
            for task in tasks
        ]

    def get_scheduled_blocks(
        self,
        start_date: str,
        number_of_days: int = 7,
    ):
        if number_of_days < 1 or number_of_days > 90:
            raise ValueError("number_of_days must be between 1 and 90.")

        start = date.fromisoformat(start_date)
        end = start + timedelta(days=number_of_days)

        tz = ZoneInfo(self._user_timezone)
        range_start = datetime.combine(
            start,
            datetime.min.time(),
            tzinfo=tz,
        )
        range_end = datetime.combine(
            end,
            datetime.min.time(),
            tzinfo=tz,
        )

        blocks = (
            self.db.query(ScheduledBlock)
            .join(Task)
            .filter(
                Task.user_id == self.user_id,
                Task.status == "pending",
                ScheduledBlock.start_time < range_end,
                ScheduledBlock.end_time > range_start,
            )
            .order_by(ScheduledBlock.start_time)
            .all()
        )

        return [
            {
                "task_id": block.task_id,
                "block_id": block.id,
                "title": block.task.title,
                "start": block.start_time.isoformat(),
                "end": block.end_time.isoformat(),
                "priority": block.task.priority,
            }
            for block in blocks
        ]

    def get_calendar_events(
        self,
        start_date: str,
        number_of_days: int = 7,
    ):
        credentials = get_google_credentials()

        if not credentials:
            return []

        google_calendar = GoogleCalendarService(
            credentials=credentials
        )

        start = datetime.combine(
            date.fromisoformat(start_date),
            datetime.min.time(),
        ).replace(tzinfo=timezone.utc)

        end = start + timedelta(
            days=number_of_days
        )

        return google_calendar.get_events(
            start_time=start,
            end_time=end,
        )

    def generate_schedule(
        self,
        start_date: str,
        number_of_days: int = 7,
    ):
        service = ScheduleService(self.db)

        schedule = service.generate_schedule(
            user_id=self.user_id,
            start_date=date.fromisoformat(start_date),
            number_of_days=number_of_days,
        )

        return {
            "items": [
                {
                    "task_id": item.task_id,
                    "title": item.title,
                    "start": item.start.isoformat(),
                    "end": item.end.isoformat(),
                    "priority": item.priority,
                }
                for item in schedule
            ],
            "total_minutes": sum(
                item.duration_minutes
                for item in schedule
            ),
        }

    def sync_schedule(
        self,
        start_date: str,
        number_of_days: int = 7,
    ):
        service = ScheduleService(self.db)

        return service.sync_schedule_to_google_calendar(
            user_id=self.user_id,
            start_date=date.fromisoformat(start_date),
            number_of_days=number_of_days,
        )

    def get_pending_tasks_for_ui(self):
        tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == self.user_id,
                Task.status == "pending",
            )
            .order_by(Task.created_at.desc())
            .all()
        )

        return [
            {
                "id": task.id,
                "title": task.title,
                "priority": task.priority,
                "estimated_minutes": task.estimated_minutes,
                "deadline": (
                    task.deadline.isoformat()
                    if task.deadline
                    else None
                ),
                "category": task.category,
                "preferred_time": task.preferred_time,
            }
            for task in tasks
        ]

    def create_reschedule_proposal(
        self,
        task_id: int,
        block_id: int,
        new_start: str,
        new_end: str,
    ):
        service = ScheduleService(self.db)

        start = datetime.fromisoformat(
            new_start.replace("Z", "+00:00")
        )

        end = datetime.fromisoformat(
            new_end.replace("Z", "+00:00")
        )

        return service.create_reschedule_proposal(
            user_id=self.user_id,
            task_id=task_id,
            block_id=block_id,
            new_start=start,
            new_end=end,
        )

    def approve_reschedule_proposal(
        self,
        proposal_id: int,
    ):
        service = ScheduleService(self.db)
        return service.approve_reschedule_proposal(
            user_id=self.user_id,
            proposal_id=proposal_id,
        )

    def reject_reschedule_proposal(
        self,
        proposal_id: int,
    ):
        service = ScheduleService(self.db)
        return service.reject_reschedule_proposal(
            user_id=self.user_id,
            proposal_id=proposal_id,
        )

    def _extract_conflict_request(self, message: str):
        """
        Detect appointment-style requests such as:

        "I have a doctor appointment today from 6 PM to 7 PM."
        "I have a meeting tomorrow from 10 AM to 11 AM."

        Returns:
            (start_time, end_time) as ISO strings
            or None if no appointment time range is detected.
        """

        text = message.lower().strip()

        # Only perform deterministic conflict checking when the user
        # appears to be talking about a fixed calendar activity.
        activity_keywords = [
            "appointment",
            "doctor",
            "meeting",
            "interview",
            "class",
            "event",
            "appointment",
        ]

        if not any(keyword in text for keyword in activity_keywords):
            return None

        # Match:
        # today from 6 PM to 7 PM
        # tomorrow from 10 AM to 11 AM
        # today 6 PM to 7 PM
        pattern = re.search(
            r"\b(today|tomorrow)\b"
            r"(?:\s+from)?\s+"
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)"
            r"\s*(?:to|-)\s*"
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b",
            text,
        )

        if not pattern:
            return None

        day_name = pattern.group(1)

        start_hour = int(pattern.group(2))
        start_minute = int(pattern.group(3) or 0)
        start_ampm = pattern.group(4)

        end_hour = int(pattern.group(5))
        end_minute = int(pattern.group(6) or 0)
        end_ampm = pattern.group(7)

        # Convert 12-hour time to 24-hour time.
        if start_ampm == "pm" and start_hour != 12:
            start_hour += 12
        elif start_ampm == "am" and start_hour == 12:
            start_hour = 0

        if end_ampm == "pm" and end_hour != 12:
            end_hour += 12
        elif end_ampm == "am" and end_hour == 12:
            end_hour = 0

        # Use the user's configured timezone.
        timezone_name = getattr(
            self,
            "_user_timezone",
            "Asia/Kolkata",
        )

        try:
            tz = ZoneInfo(timezone_name)
        except Exception:
            tz = ZoneInfo("Asia/Kolkata")

        now = datetime.now(tz)

        if day_name == "today":
            appointment_date = now.date()
        else:
            appointment_date = now.date() + timedelta(days=1)

        start = datetime(
            appointment_date.year,
            appointment_date.month,
            appointment_date.day,
            start_hour,
            start_minute,
            tzinfo=tz,
        )

        end = datetime(
            appointment_date.year,
            appointment_date.month,
            appointment_date.day,
            end_hour,
            end_minute,
            tzinfo=tz,
        )

        if end <= start:
            return None

        return start.isoformat(), end.isoformat()

    def run(self, message: str):
        tools = create_calendar_tools(
            get_tasks_fn=self.get_tasks,
            get_calendar_events_fn=self.get_calendar_events,
            generate_schedule_fn=self.generate_schedule,
            sync_schedule_fn=self.sync_schedule,
            create_reschedule_proposal_fn=self.create_reschedule_proposal,
            approve_reschedule_proposal_fn=(
                self.approve_reschedule_proposal
            ),
            reject_reschedule_proposal_fn=(
                self.reject_reschedule_proposal
            ),
            get_scheduled_blocks_fn=self.get_scheduled_blocks,
        )


        conflict_request = self._extract_conflict_request(message)

        calendar_context = ""

        if conflict_request:
            start_time, end_time = conflict_request

            # Find the actual conflict tool.
            conflict_tool = next(
                tool
                for tool in tools
                if tool.name == "check_schedule_conflict"
            )

            conflict_result = conflict_tool.invoke(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )

            calendar_context = f"""
REAL GOOGLE CALENDAR CONFLICT CHECK:

Proposed appointment:
{start_time} -> {end_time}

Calendar conflict result:
{conflict_result}

IMPORTANT:
The above result comes from the actual Google Calendar.
Do not contradict it or invent a different result.
"""

        agent = CalendarAgent(tools)

        if calendar_context:
            message_for_agent = f"""
User request:
{message}

{calendar_context}

Answer the user using the verified calendar result.
If a conflict exists, clearly identify the conflicting event.
Do not say there is no conflict when the verified result reports
a conflict.
"""
        else:
            message_for_agent = message

        return agent.run(message_for_agent)
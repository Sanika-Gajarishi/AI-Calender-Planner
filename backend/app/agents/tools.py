from datetime import datetime, timedelta
from typing import Callable

from langchain.tools import tool


def create_calendar_tools(
    get_tasks_fn: Callable,
    get_calendar_events_fn: Callable,
    generate_schedule_fn: Callable,
    sync_schedule_fn: Callable,
    reschedule_task_fn: Callable,

):
    """
    Create tools used by the AI Calendar Planner Agent.

    The actual database and Google Calendar logic stays
    inside the existing backend services.
    """

    @tool
    def get_pending_tasks() -> str:
        """
        Get the user's pending tasks.

        Use this whenever the user asks about their tasks,
        wants help planning tasks, or asks what needs to be done.
        """

        tasks = get_tasks_fn()

        if not tasks:
            return "The user has no pending tasks."

        lines = []

        for task in tasks:
            deadline = task.get("deadline")

            if deadline is None:
                deadline = "No deadline"

            lines.append(
                f"- {task['title']} | "
                f"Priority: {task.get('priority', 'medium')} | "
                f"Duration: {task.get('estimated_minutes', 0)} minutes | "
                f"Deadline: {deadline}"
            )

        return "\n".join(lines)

    @tool
    def get_google_calendar_events(
        start_date: str,
        number_of_days: int = 7,
    ) -> str:
        """
        Get existing Google Calendar events for a date range.

        Use this before planning when the user's existing
        calendar commitments matter.
        """

        events = get_calendar_events_fn(
            start_date,
            number_of_days,
        )

        if not events:
            return "There are no Google Calendar events in this period."

        lines = []

        for event in events:
            summary = event.get("summary", "Busy")

            start = event.get("start", {})
            end = event.get("end", {})

            start_value = (
                start.get("dateTime")
                or start.get("date")
                or "Unknown"
            )

            end_value = (
                end.get("dateTime")
                or end.get("date")
                or "Unknown"
            )

            lines.append(
                f"- {summary}: {start_value} -> {end_value}"
            )

        return "\n".join(lines)

    @tool
    def check_schedule_conflict(
        start_time: str,
        end_time: str,
    ) -> str:
        """
        Check whether a proposed time conflicts with
        an existing Google Calendar event.

        start_time and end_time must be ISO-8601
        datetime strings.

        Use this when the user mentions an appointment,
        meeting, doctor visit, interview, or another
        fixed time that may conflict with their schedule.
        """

        try:
            proposed_start = datetime.fromisoformat(
                start_time.replace("Z", "+00:00")
            )

            proposed_end = datetime.fromisoformat(
                end_time.replace("Z", "+00:00")
            )

            if proposed_end <= proposed_start:
                return "The end time must be after the start time."

            events = get_calendar_events_fn(
                proposed_start.date().isoformat(),
                1,
            )

            conflicts = []

            for event in events:
                event_start = event.get("start", {}).get("dateTime")
                event_end = event.get("end", {}).get("dateTime")

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

                comparison_start = proposed_start
                comparison_end = proposed_end

                if comparison_start.tzinfo is None:
                    comparison_start = comparison_start.replace(
                        tzinfo=existing_start.tzinfo
                    )
                if comparison_end.tzinfo is None:
                    comparison_end = comparison_end.replace(
                        tzinfo=existing_end.tzinfo
                    )

                if (
                    comparison_start < existing_end
                    and comparison_end > existing_start
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

            if not conflicts:
                return (
                    "No scheduling conflict found for your appointment "
                    f"from {proposed_start.strftime('%I:%M %p')} "
                    f"to {proposed_end.strftime('%I:%M %p')}."
                )

            response = "⚠️ Scheduling conflict detected.\n\n"
            response += "Your proposed appointment:\n"
            response += (
                f"• {proposed_start.strftime('%I:%M %p')} - "
                f"{proposed_end.strftime('%I:%M %p')}\n\n"
            )
            response += "Conflicting calendar events:\n"

            for conflict in conflicts:
                conflict_start = datetime.fromisoformat(
                    conflict["start"]
                )
                conflict_end = datetime.fromisoformat(
                    conflict["end"]
                )
                response += (
                    f"• {conflict['title']} — "
                    f"{conflict_start.strftime('%I:%M %p')} - "
                    f"{conflict_end.strftime('%I:%M %p')}\n"
                )

            return response
        except ValueError:
            return (
                "Invalid datetime format. "
                "Please use ISO-8601 format."
            )
        except Exception as error:
            return (
                f"Unable to check scheduling conflicts: {str(error)}"
            )

    @tool
    def find_available_time_slots(
        date_str: str,
        duration_minutes: int,
    ) -> str:
        """
        Find future available time slots on a specific date.
        Uses Asia/Kolkata timezone and checks Google Calendar events.
        Never suggests a slot in the past.
        """
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        local_tz = ZoneInfo("Asia/Kolkata")

        try:
            day = datetime.strptime(
                date_str, "%Y-%m-%d"
            ).date()
        except ValueError:
            return "Invalid date. Use YYYY-MM-DD."

        if duration_minutes <= 0:
            return "Duration must be greater than zero."

        
        now = datetime.now(local_tz)

        if day < now.date():
            return (
                f"{date_str} is in the past. "
                f"Please choose today ({now.date()}) "
                "or a future date."
            )

        try:
            events = get_calendar_events_fn(date_str, 1)
        except Exception as error:
            return f"Could not retrieve calendar events: {error}"

        working_start = datetime(
            day.year, day.month, day.day,
            9, 0, tzinfo=local_tz
        )
        working_end = datetime(
            day.year, day.month, day.day,
            22, 0, tzinfo=local_tz
        )

        if day == now.date():
            working_start = max(working_start, now)

        if working_start + timedelta(
            minutes=duration_minutes
        ) > working_end:
            return (
                f"No future {duration_minutes}-minute slot "
                f"fits within working hours on {date_str}."
            )

        busy_periods = []

        for event in events:
            event_start_data = event.get("start", {})
            event_end_data = event.get("end", {})

            start_value = (
                event_start_data.get("dateTime")
                or event_start_data.get("date")
            )
            end_value = (
                event_end_data.get("dateTime")
                or event_end_data.get("date")
            )

            if not start_value or not end_value:
                continue

            try:
                if "T" not in start_value:
                    event_start = datetime.fromisoformat(
                        start_value
                    ).replace(tzinfo=local_tz)
                    event_end = datetime.fromisoformat(
                        end_value
                    ).replace(tzinfo=local_tz)
                else:
                    event_start = datetime.fromisoformat(
                        start_value.replace("Z", "+00:00")
                    ).astimezone(local_tz)
                    event_end = datetime.fromisoformat(
                        end_value.replace("Z", "+00:00")
                    ).astimezone(local_tz)

                if event_end > event_start:
                    busy_periods.append(
                        (event_start, event_end)
                    )
            except (ValueError, TypeError):
                continue

        busy_periods.sort(key=lambda period: period[0])

        available_slots = []
        current = working_start

        for busy_start, busy_end in busy_periods:
            if busy_end <= current:
                continue

            if busy_start >= working_end:
                break

            if busy_start > current:
                candidate_end = current + timedelta(
                    minutes=duration_minutes
                )

                if candidate_end <= min(
                    busy_start, working_end
                ):
                    available_slots.append(
                        (current, candidate_end)
                    )

            current = max(current, busy_end)

            if current >= working_end:
                break

        if current < working_end:
            candidate_end = current + timedelta(
                minutes=duration_minutes
            )

            if candidate_end <= working_end:
                available_slots.append(
                    (current, candidate_end)
                )

        if not available_slots:
            return (
                f"No available {duration_minutes}-minute "
                f"slots were found on {date_str} "
                "within 9 AM–10 PM."
            )

        lines = [
            f"Available {duration_minutes}-minute slots "
            f"on {date_str} (Asia/Kolkata):"
        ]

        for start, end in available_slots[:5]:
            lines.append(
                f"- {start.isoformat()} to {end.isoformat()}"
            )

        return "\n".join(lines)

    @tool
    def reschedule_task(
        task_id: int,
        new_start: str,
        new_end: str,
    ) -> str:
        """
        Reschedule an existing scheduled task.

        Use this only when the user explicitly asks
        to move or reschedule a task.

        new_start and new_end must be ISO-8601
        datetime strings.
        """

        try:
            result = reschedule_task_fn(
                task_id,
                new_start,
                new_end,
            )

            return (
                f"Task '{result['title']}' was rescheduled "
                f"from its previous time to "
                f"{result['start']} -> {result['end']}."
            )

        except Exception as error:
            return (
                f"Unable to reschedule the task: {error}"
            )

    @tool
    def generate_smart_schedule(
        start_date: str,
        number_of_days: int = 7,
    ) -> str:
        """
        Generate an optimized schedule from the user's tasks.

        Use this when the user asks to create, plan, organize,
        or optimize their schedule.
        """

        result = generate_schedule_fn(
            start_date,
            number_of_days,
        )

        if not result.get("items"):
            return "No tasks could be scheduled."

        lines = []

        for item in result["items"]:
            lines.append(
                f"- {item['title']}: "
                f"{item['start']} -> {item['end']} "
                f"(Priority: {item['priority']})"
            )

        lines.append(
            f"Total planned time: "
            f"{result.get('total_minutes', 0)} minutes."
        )

        return "\n".join(lines)

    @tool
    def sync_schedule_to_google_calendar(
        start_date: str,
        number_of_days: int = 7,
    ) -> str:
        """
        Sync the generated schedule to Google Calendar.

        Use this only when the user explicitly asks to add,
        sync, or put the generated schedule into Google Calendar.
        """

        result = sync_schedule_fn(
            start_date,
            number_of_days,
        )

        return (
            "Google Calendar sync completed. "
            f"{result.get('created', 0)} events created and "
            f"{result.get('skipped', 0)} events skipped."
        )

    return [
        get_pending_tasks,
        get_google_calendar_events,
        check_schedule_conflict,
        find_available_time_slots,
        reschedule_task,
        generate_smart_schedule,
        sync_schedule_to_google_calendar,
    ]
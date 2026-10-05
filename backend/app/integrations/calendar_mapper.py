from datetime import datetime

from app.scheduler.models import CalendarEvent, TimeSlot


def google_event_to_calendar_event(
    event: dict,
) -> CalendarEvent | None:
    private_properties = event.get(
        "extendedProperties",
        {},
    ) or {}
    description = (event.get("description") or "").strip()

    if (
        private_properties.get("private", {}).get(
            "ai_calendar_planner"
        )
        == "scheduled_task"
        or description.startswith(
            (
                "Created by AI Calendar Planner",
                "AI Calendar Planner task",
            )
        )
    ):
        return None

    start_data = event.get("start", {})
    end_data = event.get("end", {})

    start_value = start_data.get("dateTime")
    end_value = end_data.get("dateTime")

    # Ignore all-day events for now.
    if not start_value or not end_value:
        return None

    start = datetime.fromisoformat(
        start_value.replace("Z", "+00:00")
    )

    end = datetime.fromisoformat(
        end_value.replace("Z", "+00:00")
    )

    return CalendarEvent(
        title=event.get(
            "summary",
            "Busy",
        ),
        start=start,
        end=end,
    )


def calendar_event_to_time_slot(
    event: CalendarEvent,
) -> TimeSlot:

    return TimeSlot(
        start=event.start,
        end=event.end,
    )
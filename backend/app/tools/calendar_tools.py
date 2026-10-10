from datetime import datetime, timedelta, timezone

from langchain.tools import tool

from app.integrations.google_auth import (
    get_google_credentials,
)

from app.integrations.google_calendar import (
    GoogleCalendarService,
)


def get_calendar_events_data(
    days: int = 7,
):

    credentials = get_google_credentials()

    if not credentials:
        raise ValueError(
            "Google Calendar is not connected."
        )

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

    result = []

    for event in events:

        start = event.get("start", {})
        end = event.get("end", {})

        result.append(
            {
                "id": event.get("id"),
                "title": event.get(
                    "summary",
                    "Busy",
                ),
                "start": (
                    start.get("dateTime")
                    or start.get("date")
                ),
                "end": (
                    end.get("dateTime")
                    or end.get("date")
                ),
            }
        )

    return result


def create_calendar_tools():

    @tool
    def get_calendar_events(
        days: int = 7,
    ) -> list[dict]:
        """Get existing Google Calendar events for the next specified number of days."""

        return get_calendar_events_data(
            days=days
        )

    return [
        get_calendar_events,
    ]
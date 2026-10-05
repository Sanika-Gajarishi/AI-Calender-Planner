from datetime import datetime

from app.integrations.google_auth import get_google_credentials
from app.integrations.google_calendar import GoogleCalendarService
from app.integrations.calendar_mapper import google_event_to_calendar_event
from app.scheduler.models import TimeSlot


def get_google_calendar_busy_slots(
    start_time: datetime,
    end_time: datetime,
) -> list[TimeSlot]:

    credentials = get_google_credentials()

    service = GoogleCalendarService(
        credentials=credentials
    )

    google_events = service.get_events(
        start_time=start_time,
        end_time=end_time,
    )

    busy_slots = []

    for event in google_events:
        calendar_event = google_event_to_calendar_event(event)

        if calendar_event is None:
            continue

        busy_slots.append(
            TimeSlot(
                start=calendar_event.start,
                end=calendar_event.end,
            )
        )

    return busy_slots
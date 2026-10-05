from datetime import datetime

from app.integrations.google_calendar import (
    GoogleCalendarService,
)
from app.integrations.calendar_mapper import (
    calendar_event_to_time_slot,
    google_event_to_calendar_event,
)


class CalendarService:

    def __init__(
        self,
        google_calendar: GoogleCalendarService,
    ):
        self.google_calendar = google_calendar

    def get_busy_slots(
        self,
        start: datetime,
        end: datetime,
    ):

        google_events = (
            self.google_calendar.get_events(
                start_time=start,
                end_time=end,
            )
        )

        busy_slots = []

        for google_event in google_events:

            calendar_event = (
                google_event_to_calendar_event(
                    google_event
                )
            )

            if calendar_event is None:
                continue

            busy_slots.append(
                calendar_event_to_time_slot(
                    calendar_event
                )
            )

        return busy_slots
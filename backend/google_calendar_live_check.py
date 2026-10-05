from datetime import datetime, timedelta

from app.integrations.google_auth import (
    get_google_credentials,
)
from app.integrations.google_calendar import (
    GoogleCalendarService,
)


credentials = get_google_credentials()

calendar = GoogleCalendarService(
    credentials
)

start = datetime.now().astimezone()

end = start + timedelta(days=7)

events = calendar.get_events(
    start_time=start,
    end_time=end,
)

print("\nCalendar events:\n")

for event in events:

    print(
        event.get(
            "summary",
            "No title",
        )
    )

    print(
        event.get("start")
    )

    print(
        event.get("end")
    )

    print("-" * 40)
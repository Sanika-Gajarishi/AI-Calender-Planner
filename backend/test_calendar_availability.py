from datetime import datetime, timedelta, timezone

from app.services.calendar_availability import (
    get_google_calendar_busy_slots,
)


start = datetime.now(timezone.utc)

end = start + timedelta(days=7)

slots = get_google_calendar_busy_slots(
    start_time=start,
    end_time=end,
)

print("\nGoogle Calendar Busy Slots:")

for slot in slots:
    print(
        f"{slot.start} -> {slot.end}"
    )

print(f"\nTotal busy slots: {len(slots)}")
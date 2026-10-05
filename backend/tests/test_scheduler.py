from datetime import datetime

from app.scheduler.slot_finder import generate_working_slots


def test_generate_working_slots():
    slots = generate_working_slots(
        start_date=datetime(2026, 9, 22),
        end_date=datetime(2026, 9, 22),
        work_start_hour=18,
        work_end_hour=22,
        slot_minutes=60,
    )

    assert len(slots) == 4

    assert slots[0].start.hour == 18
    assert slots[0].end.hour == 19

    assert slots[-1].start.hour == 21
    assert slots[-1].end.hour == 22
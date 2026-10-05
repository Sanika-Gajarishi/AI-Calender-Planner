from datetime import datetime
from datetime import date, time
from zoneinfo import ZoneInfo
from app.scheduler.engine import SchedulingEngine
from app.scheduler.multi_day_scheduler import(
    DailyAvailability,
    generate_multi_day_schedule,
)
from app.scheduler.models import TimeSlot

class FakeTask:
    def __init__(
        self,
        task_id,
        title,
        priority,
        estimated_minutes,
        deadline=None,
    ):
        self.id = task_id
        self.title = title
        self.priority = priority
        self.estimated_minutes = estimated_minutes
        self.deadline = deadline


def test_generate_schedule():

    tasks = [
        FakeTask(
            task_id=1,
            title="Python Practice",
            priority="medium",
            estimated_minutes=60,
        ),
        FakeTask(
            task_id=2,
            title="AI Project",
            priority="high",
            estimated_minutes=120,
        ),
    ]

    engine = SchedulingEngine()

    schedule = engine.generate_schedule(
        tasks=tasks,
        start_date=datetime(2026, 9, 22),
        end_date=datetime(2026, 9, 22),
        work_start_hour=18,
        work_end_hour=22,
        slot_minutes=60,
    )

    assert len(schedule) == 3

    assert schedule[0].title == "AI Project"
    assert schedule[1].title == "AI Project"
    assert schedule[2].title == "Python Practice"


def test_multi_day_scheduler_splits_large_task():

    task = FakeTask(
        task_id=1,
        title="AI Project",
        priority="high",
        estimated_minutes=360,
    )

    days = [
        DailyAvailability(
            date=date(2026, 9, 22),
            work_start=time(18, 0),
            work_end=time(22, 0),
            busy_slots=[],
        ),
        DailyAvailability(
            date=date(2026, 9, 23),
            work_start=time(18, 0),
            work_end=time(22, 0),
            busy_slots=[],
        ),
    ]

    schedule = generate_multi_day_schedule(
        tasks=[task],
        days=days,
        max_daily_hours=4,
    )

    total_minutes = sum(
        item.duration_minutes
        for item in schedule
    )

    assert total_minutes == 360

    first_day_minutes = sum(
        item.duration_minutes
        for item in schedule
        if item.start.date() == date(2026, 9, 22)
    )

    second_day_minutes = sum(
        item.duration_minutes
        for item in schedule
        if item.start.date() == date(2026, 9, 23)
    )

    assert first_day_minutes <= 240
    assert second_day_minutes <= 240

def test_multi_day_scheduler_respects_busy_time():

    task = FakeTask(
        task_id=1,
        title="Python Practice",
        priority="high",
        estimated_minutes=180,
    )

    busy_slot = TimeSlot(
        start=datetime(
            2026,
            9,
            22,
            19,
            0,
        ),
        end=datetime(
            2026,
            9,
            22,
            20,
            0,
        ),
    )

    days = [
        DailyAvailability(
            date=date(2026, 9, 22),
            work_start=time(18, 0),
            work_end=time(22, 0),
            busy_slots=[busy_slot],
        ),
    ]

    schedule = generate_multi_day_schedule(
        tasks=[task],
        days=days,
        max_daily_hours=4,
    )

    for item in schedule:

        assert not (
            item.start < busy_slot.end
            and item.end > busy_slot.start
        )



def test_scheduler_does_not_schedule_over_calendar_event():

    task = FakeTask(
        task_id=1,
        title="AI Project",
        priority="high",
        estimated_minutes=120,
    )

    busy_slot = TimeSlot(
        start=datetime(
            2026,
            9,
            22,
            19,
            0,
        ),
        end=datetime(
            2026,
            9,
            22,
            20,
            0,
        ),
    )

    days = [
        DailyAvailability(
            date=date(2026, 9, 22),
            work_start=time(18, 0),
            work_end=time(22, 0),
            busy_slots=[busy_slot],
        )
    ]

    schedule = generate_multi_day_schedule(
        tasks=[task],
        days=days,
        max_daily_hours=4,
    )

    for item in schedule:

        overlaps = (
            item.start < busy_slot.end
            and item.end > busy_slot.start
        )

        assert overlaps is False


def test_multi_day_scheduler_handles_timezone_aware_busy_slots():
    task = FakeTask(
        task_id=1,
        title="AI Project",
        priority="high",
        estimated_minutes=60,
    )
    busy_slot = TimeSlot(
        start=datetime.fromisoformat("2026-09-22T12:30:00+00:00"),
        end=datetime.fromisoformat("2026-09-22T13:30:00+00:00"),
    )
    days = [
        DailyAvailability(
            date=date(2026, 9, 22),
            work_start=time(18, 0),
            work_end=time(22, 0),
            busy_slots=[busy_slot],
            timezone=ZoneInfo("Asia/Kolkata"),
        ),
    ]

    schedule = generate_multi_day_schedule(
        tasks=[task],
        days=days,
        max_daily_hours=4,
    )

    assert len(schedule) == 1
    assert schedule[0].start.isoformat() == "2026-09-22T19:00:00+05:30"
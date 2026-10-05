from datetime import datetime

from app.integrations.calendar_mapper import (
    calendar_event_to_time_slot,
    google_event_to_calendar_event,
)
from app.scheduler.models import TimeSlot


def test_google_event_conversion():

    google_event = {
        "summary": "Team Meeting",
        "start": {
            "dateTime": "2026-09-22T19:00:00+05:30"
        },
        "end": {
            "dateTime": "2026-09-22T20:00:00+05:30"
        },
    }

    event = google_event_to_calendar_event(
        google_event
    )

    assert event is not None

    assert event.title == "Team Meeting"

    assert event.start == datetime.fromisoformat(
        "2026-09-22T19:00:00+05:30"
    )

    assert event.end == datetime.fromisoformat(
        "2026-09-22T20:00:00+05:30"
    )



def test_google_event_becomes_busy_slot():

    google_event = {
        "summary": "Interview",
        "start": {
            "dateTime": "2026-09-22T19:00:00+05:30"
        },
        "end": {
            "dateTime": "2026-09-22T20:00:00+05:30"
        },
    }

    calendar_event = google_event_to_calendar_event(
        google_event
    )

    assert calendar_event is not None

    busy_slot = calendar_event_to_time_slot(
        calendar_event
    )

    assert busy_slot.start == datetime.fromisoformat(
        "2026-09-22T19:00:00+05:30"
    )

    assert busy_slot.end == datetime.fromisoformat(
        "2026-09-22T20:00:00+05:30"
    )


def test_ai_calendar_planner_event_is_not_a_busy_slot():
    google_event = {
        "summary": "Prepare for interview",
        "description": (
            "Created by AI Calendar Planner\n"
            "Task ID: 1"
        ),
        "extendedProperties": {
            "private": {
                "ai_calendar_planner": "scheduled_task",
            },
        },
        "start": {
            "dateTime": "2026-09-22T19:00:00+05:30"
        },
        "end": {
            "dateTime": "2026-09-22T20:00:00+05:30"
        },
    }

    event = google_event_to_calendar_event(
        google_event
    )

    assert event is None


def test_legacy_ai_calendar_planner_event_is_not_a_busy_slot():
    google_event = {
        "summary": "Prepare for interview",
        "description": (
            "AI Calendar Planner task\n"
            "Task ID: 1"
        ),
        "start": {
            "dateTime": "2026-09-22T19:00:00+05:30"
        },
        "end": {
            "dateTime": "2026-09-22T20:00:00+05:30"
        },
    }

    event = google_event_to_calendar_event(
        google_event
    )

    assert event is None
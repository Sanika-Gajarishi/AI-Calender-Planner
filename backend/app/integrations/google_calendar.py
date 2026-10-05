from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


GOOGLE_CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


class GoogleCalendarService:

    def __init__(self, credentials: Credentials):
        self.credentials = credentials

        self.service = build(
            "calendar",
            "v3",
            credentials=self.credentials,
        )

    def get_events(
        self,
        start_time: datetime,
        end_time: datetime,
    ):

        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=start_time.astimezone(
                    timezone.utc
                ).isoformat(),
                timeMax=end_time.astimezone(
                    timezone.utc
                ).isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get(
            "items",
            []
        )

    def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str | None = None,
    ):

        event = {
            "summary": title,
            "description": description or "",
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
        }

        created_event = (
            self.service.events()
            .insert(
                calendarId="primary",
                body=event,
            )
            .execute()
        )

        return created_event

    def create_scheduled_task_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str | None = None,
    ):
        event = {
            "summary": title,
            "description": description or "Created by AI Calendar Planner",
            "extendedProperties": {
                "private": {
                    "ai_calendar_planner": "scheduled_task",
                },
            },
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
        }

        created_event = (
            self.service.events()
            .insert(
                calendarId="primary",
                body=event,
            )
            .execute()
        )

        return created_event

    def delete_event(
        self,
        event_id: str,
    ):
        self.service.events().delete(
            calendarId="primary",
            eventId=event_id,
        ).execute()
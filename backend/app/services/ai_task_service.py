from datetime import datetime
import json

from app.schemas.ai_task import (
    TaskUnderstandingResponse,
)
from app.services.gemini_service import (
    GeminiService,
)


class AITaskService:

    def __init__(self):
        self.gemini = GeminiService()

    def understand_task(
        self,
        text: str,
        current_datetime: datetime | None = None,
        timezone: str = "Asia/Kolkata",
    ) -> TaskUnderstandingResponse:

        if current_datetime is None:
            current_datetime = datetime.now()

        current_date = current_datetime.date().isoformat()
        current_time = current_datetime.strftime("%H:%M")

        prompt = f"""
You are an AI task understanding assistant
for an intelligent calendar planner.

CURRENT APPLICATION DATE:
{current_date}

CURRENT APPLICATION TIME:
{current_time}

USER TIMEZONE:
{timezone}

Use the current date and timezone above when
interpreting relative dates such as:

- today
- tomorrow
- this Friday
- next Friday
- next week
- in 3 days
- in 2 weeks

USER REQUEST:

{text}

Return ONLY valid JSON.

The JSON must contain exactly these fields:

title:
A short and clear task title.

description:
A concise description of the task.

priority:
Must be one of:
low
medium
high

estimated_minutes:
Estimated total time required for the task.
Return an integer number of minutes.

deadline:
Return an ISO-8601 datetime if a deadline
is explicitly or relatively provided.

If no deadline is provided, return null.

preferred_time:
Must be one of:
morning
afternoon
evening
night
or null.

category:
Choose a useful category such as:
work
study
interview
project
personal
health
other

Choose the category based on the task's primary goal,
not the activity used to complete it. For example, preparing
for an interview is category "interview", even when the user
describes studying or practicing as the preparation activity.

Rules:

1. Do not invent information.

2. Use the provided current date when
interpreting relative dates.

3. Convert hours to minutes.

Example:
2 hours = 120.

4. Convert minutes directly.

5. Keep the title concise.

6. If priority is not explicitly mentioned,
use "medium".

7. If a preferred time is not mentioned,
return null.

8. Return ONLY JSON.
"""

        response = self.gemini.generate_json(prompt)

        data = json.loads(response)

        return TaskUnderstandingResponse(**data)
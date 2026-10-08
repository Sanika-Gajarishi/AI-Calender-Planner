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
interpreting relative dates and times.

Examples of relative dates:

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
Must be exactly one of:
low
medium
high

If priority is not explicitly mentioned,
use "medium".

estimated_minutes:
Estimated total time required for the task.
Return an integer number of minutes.

Examples:
2 hours = 120
1.5 hours = 90
30 minutes = 30

deadline:
The date and time by which the task should
be completed.

Return an ISO-8601 datetime when the user
explicitly or relatively provides a deadline.

Examples:

"finish this by October 10"
→ deadline should be October 10.

"complete this tomorrow"
→ deadline should be tomorrow.

"I need this done by Friday at 6 PM"
→ deadline should be Friday at 18:00.

"submit it in 3 days"
→ deadline should be current date + 3 days.

"finish this by tomorrow evening"
→ deadline should be tomorrow evening.

IMPORTANT:
Only set a deadline when the user's request
indicates that the task itself must be completed
by that date or time.

Do NOT automatically treat an unrelated event date
as the task deadline.

For example:

"I have an interview on October 12 and need
to prepare for it."

The interview date is context for the task.
Treat October 12 as the deadline for preparation
only when the wording indicates that preparation
should be completed before the interview.

If the user does not provide enough information
to determine a deadline, return null.

preferred_time:
Must be exactly one of:
morning
afternoon
evening
night
or null.

Only set preferred_time when the user indicates
when they prefer to work on the task.

category:
Choose a useful category such as:
work
study
interview
project
personal
health
other

Choose the category based on the task's
primary goal, not the activity used to complete it.

For example:
"Practice Python for my interview"
→ category = "interview"

"Build my AI Calendar Planner"
→ category = "project"

Rules:

1. Do not invent information.

2. Use the provided current date and time when
interpreting relative dates.

3. Respect the user's timezone.

4. Convert hours to minutes.

5. Keep the title concise.

6. If priority is not explicitly mentioned,
use "medium".

7. If a preferred time is not mentioned,
return null.

8. If a deadline is not provided or cannot be
determined reliably, return null.

9. Never use a date from unrelated context as
the deadline unless the wording indicates that
the task should be completed by that date.

10. Return ONLY valid JSON.

11. Do not include markdown.

12. Do not include explanations outside the JSON.
"""

        response = self.gemini.generate_json(prompt)

        data = json.loads(response)

        return TaskUnderstandingResponse(**data)
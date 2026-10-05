from datetime import datetime

from app.services.ai_task_service import (
    AITaskService,
)


def test_understand_task():

    service = AITaskService()

    result = service.understand_task(
        """
        I have an AI interview next Friday.
        I need 8 hours to prepare.
        This is high priority.
        I prefer studying in the evening.
        """,
        current_datetime=datetime(
            2026,
            10,
            1,
            14,
            0,
        ),
        timezone="Asia/Kolkata",
    )

    print("\nAI TASK:")
    print(
        result.model_dump_json(
            indent=2
        )
    )

    assert result.title

    assert (
        result.estimated_minutes == 480
    )

    assert result.priority == "high"

    assert (
        result.preferred_time
        == "evening"
    )

    assert result.category == "interview"

    assert result.deadline is not None
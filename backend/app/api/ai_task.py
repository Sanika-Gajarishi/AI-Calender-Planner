from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from google.genai import errors
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_user

from app.models.user import User

from app.schemas.ai_task import (
    TaskUnderstandingRequest,
    TaskUnderstandingResponse,
)

from app.services.ai_task_service import (
    AITaskService,
)

from app.services.task_service import (
    TaskService,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/create-task",
)
def create_ai_task(
    request: TaskUnderstandingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    ai_service = AITaskService()

    try:
        task_data = ai_service.understand_task(
            request.text,
            timezone=current_user.timezone,
        )
    except errors.ServerError:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI service is temporarily unavailable. "
                "Please try again in a moment."
            ),
        )

    task = TaskService.create_task_from_ai(
        db=db,
        user_id=current_user.id,
        task_data=task_data,
    )

    return {
        "message": "Task created successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "deadline": task.deadline,
            "estimated_minutes": task.estimated_minutes,
            "category": task.category,
            "preferred_time": task.preferred_time,
            "status": task.status,
        },
    }
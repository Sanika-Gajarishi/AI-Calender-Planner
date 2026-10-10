from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.agent_service import AgentService


router = APIRouter(
    prefix="/agent",
    tags=["AI Calendar Agent"],
)


@router.post("/chat")
def chat_with_calendar_agent(
    message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AgentService(
        db=db,
        user_id=current_user.id,
    )

    response = service.run(message)

    result = {
        "message": response,
    }

    if any(
        keyword in message.lower()
        for keyword in [
            "what tasks",
            "my tasks",
            "pending tasks",
            "show tasks",
            "list tasks",
        ]
    ):
        result["tasks"] = service.get_pending_tasks_for_ui()

    return result
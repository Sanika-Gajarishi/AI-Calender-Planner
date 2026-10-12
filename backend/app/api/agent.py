from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel

from app.services.schedule_service import ScheduleService
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.agent_service import AgentService


class CreateRescheduleProposalRequest(BaseModel):
    task_id: int
    block_id: int
    new_start: datetime
    new_end: datetime


class RescheduleProposalActionRequest(BaseModel):
    proposal_id: int



router = APIRouter(
    prefix="/agent",
    tags=["AI Calendar Agent"],
)

@router.post("/reschedule-proposals")
def create_reschedule_proposal(
    request: CreateRescheduleProposalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ScheduleService(db)

    try:
        return service.create_reschedule_proposal(
            user_id=current_user.id,
            task_id=request.task_id,
            block_id=request.block_id,
            new_start=request.new_start,
            new_end=request.new_end,
        )
    except ValueError as error:
        message = str(error)
        status_code = (
            404 if "not found" in message.lower() else 400
        )
        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error


@router.post("/reschedule-proposals/approve")
def approve_reschedule_proposal(
    request: RescheduleProposalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ScheduleService(db)

    try:
        return service.approve_reschedule_proposal(
            user_id=current_user.id,
            proposal_id=request.proposal_id,
        )
    except ValueError as error:
        message = str(error)
        lowered = message.lower()

        if "not found" in lowered:
            status_code = 404
        elif "conflict" in lowered or "already" in lowered:
            status_code = 409
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error


@router.post("/reschedule-proposals/reject")
def reject_reschedule_proposal(
    request: RescheduleProposalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ScheduleService(db)

    try:
        return service.reject_reschedule_proposal(
            user_id=current_user.id,
            proposal_id=request.proposal_id,
        )
    except ValueError as error:
        message = str(error)
        status_code = (
            404 if "not found" in message.lower() else 409
        )
        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error

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
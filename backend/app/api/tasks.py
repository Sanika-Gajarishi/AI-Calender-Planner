from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.models.scheduled_block import ScheduledBlock
from app.integrations.google_auth import get_google_credentials
from app.integrations.google_calendar import GoogleCalendarService

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        deadline=task_data.deadline,
        estimated_minutes=task_data.estimated_minutes,
        category=task_data.category,
        preferred_time=task_data.preferred_time,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
        .all()
    )

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == current_user.id,
        )
        .first()
    )
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == current_user.id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    update_data = task_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.user_id == current_user.id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    scheduled_blocks = (
        db.query(ScheduledBlock)
        .filter(ScheduledBlock.task_id == task.id)
        .all()
    )

    credentials = get_google_credentials()

    if credentials:
        google_calendar = GoogleCalendarService(
            credentials=credentials
        )

        for block in scheduled_blocks:
            if block.google_event_id:
                try:
                    google_calendar.delete_event(
                        block.google_event_id
                    )
                except Exception as error:
                    # The event may already have been deleted in Google Calendar.
                    print(
                        f"Could not delete Google event "
                        f"{block.google_event_id}: {error}"
                    )

    db.delete(task)
    db.commit()

    return {
        "message": (
            "Task and associated Google Calendar events "
            "deleted successfully"
        )
    }
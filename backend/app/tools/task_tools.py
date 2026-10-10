from langchain.tools import tool
from sqlalchemy.orm import Session

from app.models.task import Task


def get_my_tasks_data(
    db: Session,
    user_id: int,
):
    tasks = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.status == "pending",
        )
        .order_by(Task.deadline.asc())
        .all()
    )

    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "deadline": (
                task.deadline.isoformat()
                if task.deadline
                else None
            ),
            "estimated_minutes": task.estimated_minutes,
            "category": task.category,
            "preferred_time": task.preferred_time,
        }
        for task in tasks
    ]


def create_task_tools(
    db: Session,
    user_id: int,
):

    @tool
    def get_my_tasks() -> list[dict]:
        """Get all pending tasks belonging to the current user."""

        return get_my_tasks_data(
            db=db,
            user_id=user_id,
        )

    return [
        get_my_tasks,
    ]
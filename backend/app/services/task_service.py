from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.ai_task import TaskUnderstandingResponse


class TaskService:

    @staticmethod
    def create_task_from_ai(
        db: Session,
        user_id: int,
        task_data: TaskUnderstandingResponse,
    ) -> Task:

        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            deadline=task_data.deadline,
            estimated_minutes=task_data.estimated_minutes,
            category=task_data.category,
            preferred_time=task_data.preferred_time,
            status="pending",
        )

        db.add(task)

        db.commit()

        db.refresh(task)

        return task
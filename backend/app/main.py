from fastapi import FastAPI
from app.api.agent import router as agent_router
from app.api.calendar import router as calendar_router
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.users import router as users_router
from app.database.base import Base
from app.database.connection import engine
from app.api.preferences import router as preferences_router
from app.api.schedule import router as schedule_router
from app.api.ai_task import router as ai_task_router
from app.models.scheduled_block import ScheduledBlock
app = FastAPI(
    title="AI Calendar Planner",
    description="Intelligent AI-powered scheduling system",
    version="1.0.0",
)


try:
    Base.metadata.create_all(bind=engine)
    user_columns = {
        column["name"]
        for column in inspect(engine).get_columns("users")
    }
    if "hashed_password" not in user_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN hashed_password VARCHAR(255)"
                )
            )

    scheduled_block_columns = {
        column["name"]
        for column in inspect(engine).get_columns(
            "scheduled_blocks"
        )
    }
    if "google_event_id" not in scheduled_block_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE scheduled_blocks "
                    "ADD COLUMN google_event_id VARCHAR"
                )
            )

    for index in ScheduledBlock.__table__.indexes:
        if any(
            column.name == "google_event_id"
            for column in index.columns
        ):
            index.create(
                bind=engine,
                checkfirst=True,
            )
except OperationalError:
    pass


app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(preferences_router)
app.include_router(schedule_router)
app.include_router(auth_router)
app.include_router(
    ai_task_router
)
app.include_router(calendar_router)
app.include_router(agent_router)

@app.get("/")
def root():
    return {
        "message": "AI Calendar Planner API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
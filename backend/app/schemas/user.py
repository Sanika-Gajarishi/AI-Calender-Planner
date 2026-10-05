from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    timezone: str = "Asia/Kolkata"


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    google_id: str | None
    timezone: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
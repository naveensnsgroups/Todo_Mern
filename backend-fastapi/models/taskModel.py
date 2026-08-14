from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    user_id: str = Field(..., alias='userId')
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    completed: Optional[bool] = None

class TaskInDB(TaskBase):
    id: str = Field(..., alias='_id')
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z" if dt.tzinfo else dt.isoformat() + "Z"
        }
        from_attributes = True
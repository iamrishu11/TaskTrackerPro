from pydantic import BaseModel, validator
from typing import Optional
from datetime import date

class TaskCreateSchema(BaseModel):
    task_name: str
    description: Optional[str] = ""
    status: Optional[bool] = True
    priority: str
    created_at: date
    assigned_user: str

    @validator('priority')
    def validate_priority(cls, value):
        if value.lower() not in ['low', 'medium', 'high']:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
        return value.lower()


class TaskUpdateSchema(BaseModel):
    task_name: Optional[str]
    description: Optional[str]
    status: Optional[bool]
    priority: Optional[str]
    created_at: Optional[date]
    assigned_user: Optional[str]

    @validator("priority")
    def validate_priority(cls, v):
        if v and v.lower() not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
        return v.lower() if v else v

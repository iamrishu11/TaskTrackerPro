from pydantic import BaseModel, field_validator , ConfigDict
from typing import Optional
from datetime import date

class TaskCreateSchema(BaseModel):
    task_name: str
    description: Optional[str] = ""
    status: Optional[bool] = True
    priority: str
    created_at: date
    assigned_user: str

    @field_validator('priority')
    def validate_priority(cls, value):
        if value.lower() not in ['low', 'medium', 'high']:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
        return value.lower()


class TaskUpdateSchema(BaseModel):
    task_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None
    priority: Optional[str] = None
    created_at: Optional[date] = None
    assigned_user: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("priority")
    def validate_priority(cls, v):
        if v and v.lower() not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
        return v.lower() if v else v


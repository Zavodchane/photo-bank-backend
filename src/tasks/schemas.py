import enum
from typing import Optional, Any

from pydantic import BaseModel
from fastapi import HTTPException


class Status(str, enum.Enum):
    failure: str = "failure"
    in_progress: str = "in progress"
    completed: str = "completed"


class Response(BaseModel):
    data: dict
    status: Status


class Task(BaseModel):
    task_id: Optional[str] = None
    detail: Optional[str] = None

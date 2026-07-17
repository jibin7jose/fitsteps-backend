from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GoalBase(BaseModel):
    goal_type: str
    target: int
    frequency: str

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    target: Optional[int] = None
    frequency: Optional[str] = None

class GoalResponse(GoalBase):
    id: int
    user_id: int
    start_date: datetime

    class Config:
        from_attributes = True

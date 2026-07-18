from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivityBase(BaseModel):
    goal_id: Optional[int] = None
    category: Optional[str] = "walking"
    steps: Optional[int] = 0
    duration: Optional[int] = 0
    notes: Optional[str] = None

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    id: int
    user_id: int
    activity_date: datetime

    class Config:
        from_attributes = True

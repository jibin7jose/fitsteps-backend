from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BadgeBase(BaseModel):
    name: str
    description: str
    icon_url: Optional[str] = None

class BadgeResponse(BadgeBase):
    id: int
    
    class Config:
        from_attributes = True

class UserBadgeResponse(BaseModel):
    id: int
    earned_at: datetime
    badge: BadgeResponse

    class Config:
        from_attributes = True

class GamificationSummary(BaseModel):
    current_streak: int
    longest_streak: int
    last_active_date: Optional[datetime] = None
    earned_badges: List[UserBadgeResponse]

    class Config:
        from_attributes = True

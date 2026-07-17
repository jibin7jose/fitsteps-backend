from pydantic import BaseModel
from typing import List, Optional

class AIRecommendationResponse(BaseModel):
    recommended_steps: int
    reason: str
    activity_breaks: Optional[List[str]] = []
    motivation_trend: Optional[str] = ""

from pydantic import BaseModel

class AIRecommendationResponse(BaseModel):
    recommended_steps: int
    reason: str

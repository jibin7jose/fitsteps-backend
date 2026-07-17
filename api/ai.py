from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import google.generativeai as genai
import json
from datetime import datetime, timedelta
from core.config import settings
from db.database import get_db
from db import models
from schemas import ai as ai_schema
from api.dependencies import get_current_user

router = APIRouter()

genai.configure(api_key=settings.GEMINI_API_KEY)

@router.post("/recommendation", response_model=ai_schema.AIRecommendationResponse)
def get_recommendation(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Get last 7 days of activities
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    activities = db.query(models.Activity).filter(
        models.Activity.user_id == current_user.id,
        models.Activity.activity_date >= seven_days_ago
    ).all()
    
    activity_summary = []
    for a in activities:
        activity_summary.append({
            "date": a.activity_date.isoformat(),
            "category": a.category,
            "steps": a.steps,
            "duration": a.duration
        })
    
    prompt = f"""
    The user has the following activities over the last 7 days:
    {json.dumps(activity_summary, indent=2)}
    
    Recommend a realistic step goal for tomorrow based on this history.
    Respond ONLY in valid JSON format with the following keys:
    "recommended_steps" (integer)
    "reason" (string explaining why, keep it encouraging)
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        result = json.loads(text)
        
        # Save recommendation to DB
        recommendation = models.AIRecommendation(
            user_id=current_user.id,
            recommended_steps=result.get("recommended_steps", 10000),
            reason=result.get("reason", "Keep moving!")
        )
        db.add(recommendation)
        db.commit()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI recommendation: {str(e)}")

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
            "duration": a.duration,
            "notes": a.notes
        })
    
    prompt = f"""
    The user has the following activities over the last 7 days:
    {json.dumps(activity_summary, indent=2)}
    
    Based on this history, please provide:
    1. A realistic daily step goal for tomorrow.
    2. An encouraging reason.
    3. 2 short, context-aware activity breaks to suggest (e.g., '5-min walk after sitting').
    4. Analyze any 'notes' for motivation trends and provide an encouraging insight.
    
    Respond ONLY in valid JSON format with the following keys:
    "recommended_steps" (integer),
    "reason" (string),
    "activity_breaks" (array of strings),
    "motivation_trend" (string)
    """
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        result = json.loads(text)
        
        # Save recommendation to DB (only basic fields exist in DB schema)
        recommendation = models.AIRecommendation(
            user_id=current_user.id,
            recommended_steps=result.get("recommended_steps", 10000),
            reason=result.get("reason", "Keep moving!")
        )
        db.add(recommendation)
        db.commit()
        
        # Ensure new fields are in the result
        if "activity_breaks" not in result:
            result["activity_breaks"] = ["Take a 5-minute stretch break every 2 hours."]
        if "motivation_trend" not in result:
            result["motivation_trend"] = "Consistency is key. Keep up the great work!"
            
        return result
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota exceeded" in error_msg:
            print("Gemini API rate limit exceeded, using fallback recommendation.")
            result = {
                "recommended_steps": 10000,
                "reason": "Keep up the great work!",
                "activity_breaks": ["Take a 5-min walk after sitting for 2 hours.", "Stretch your legs! "],
                "motivation_trend": "You are doing great, keep going!"
            }
            recommendation = models.AIRecommendation(
                user_id=current_user.id,
                recommended_steps=result["recommended_steps"],
                reason=result["reason"]
            )
            db.add(recommendation)
            db.commit()
            return result
            
        raise HTTPException(status_code=500, detail=f"Failed to get AI recommendation: {error_msg}")

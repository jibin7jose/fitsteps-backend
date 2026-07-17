from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from db.database import get_db
from db import models
from api.dependencies import get_current_user
from sqlalchemy import func

router = APIRouter()

@router.get("/")
def get_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Calculate weekly step average
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    activities = db.query(models.Activity).filter(
        models.Activity.user_id == current_user.id,
        models.Activity.activity_date >= seven_days_ago
    ).all()
    
    total_steps = sum(a.steps for a in activities)
    weekly_average = total_steps / 7 if activities else 0
    
    # Calculate best day (max steps)
    best_day = db.query(
        func.date(models.Activity.activity_date).label('date'),
        func.sum(models.Activity.steps).label('total_steps')
    ).filter(
        models.Activity.user_id == current_user.id
    ).group_by(
        func.date(models.Activity.activity_date)
    ).order_by(
        func.sum(models.Activity.steps).desc()
    ).first()
    
    best_day_steps = best_day.total_steps if best_day else 0
    best_day_date = best_day.date if best_day else None
    
    return {
        "weekly_step_average": round(weekly_average, 2),
        "best_day": {
            "date": best_day_date,
            "steps": best_day_steps
        }
    }

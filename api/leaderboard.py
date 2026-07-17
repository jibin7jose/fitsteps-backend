from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from db.database import get_db
from db import models
from api.dependencies import get_current_user

router = APIRouter()

@router.get("/")
def get_leaderboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Query all users and calculate their steps in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    users = db.query(models.User).all()
    
    leaderboard_data = []
    
    for user in users:
        activities = db.query(models.Activity).filter(
            models.Activity.user_id == user.id,
            models.Activity.activity_date >= seven_days_ago
        ).all()
        
        steps = sum(a.steps for a in activities)
        
        is_current = (user.id == current_user.id)
        name_display = user.name + " (You)" if is_current else user.name
        
        leaderboard_data.append({
            "id": user.id,
            "name": name_display,
            "steps": steps,
            "is_current_user": is_current
        })
    
    # Sort by steps descending
    leaderboard = sorted(leaderboard_data, key=lambda x: x["steps"], reverse=True)
    
    # Add ranks
    for index, friend in enumerate(leaderboard):
        friend["rank"] = index + 1
        
    return leaderboard

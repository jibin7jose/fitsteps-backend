from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from db.database import get_db
from db import models
from api.dependencies import get_current_user
from sqlalchemy import func, text

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
        text('1')
    ).order_by(
        func.sum(models.Activity.steps).desc()
    ).first()
    
    best_day_steps = best_day.total_steps if best_day else 0
    best_day_date = best_day.date if best_day else None
    
    # Goal Completion Rate (Today)
    goal = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id,
        models.Goal.goal_type == 'daily_steps'
    ).first()
    
    goal_completion_rate = 0
    if goal and goal.target > 0:
        target = goal.target
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_activities = db.query(models.Activity).filter(
            models.Activity.user_id == current_user.id,
            models.Activity.activity_date >= today_start
        ).all()
        
        today_steps = sum(a.steps for a in today_activities)
        goal_completion_rate = min(100, round((today_steps / target) * 100))
        
    # Calculate best week (max steps)
    best_week = db.query(
        func.date_trunc('week', models.Activity.activity_date).label('week'),
        func.sum(models.Activity.steps).label('total_steps')
    ).filter(
        models.Activity.user_id == current_user.id
    ).group_by(
        text('1')
    ).order_by(
        func.sum(models.Activity.steps).desc()
    ).first()
    
    best_week_steps = best_week.total_steps if best_week else 0
    best_week_date = best_week.week if best_week else None
        
    return {
        "weekly_step_average": round(weekly_average, 2),
        "best_day": {
            "date": best_day_date,
            "steps": best_day_steps
        },
        "best_week": {
            "date": best_week_date,
            "steps": best_week_steps
        },
        "goal_completion_rate": goal_completion_rate
    }

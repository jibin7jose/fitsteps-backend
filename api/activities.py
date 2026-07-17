from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import csv
import io
from db.database import get_db
from db import models
from schemas import activity as activity_schema
from api.dependencies import get_current_user

router = APIRouter()

from datetime import datetime, timedelta

@router.post("/", response_model=activity_schema.ActivityResponse)
def create_activity(activity: activity_schema.ActivityCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if activity.goal_id:
        goal = db.query(models.Goal).filter(models.Goal.id == activity.goal_id, models.Goal.user_id == current_user.id).first()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found or does not belong to user")
            
    new_activity = models.Activity(**activity.model_dump(), user_id=current_user.id)
    db.add(new_activity)
    
    # Gamification Logic
    now = datetime.utcnow()
    last_active = current_user.last_active_date

    if last_active:
        delta_days = (now.date() - last_active.date()).days
        if delta_days == 1:
            current_user.current_streak += 1
        elif delta_days > 1:
            current_user.current_streak = 1
    else:
        current_user.current_streak = 1
    
    if current_user.current_streak > current_user.longest_streak:
        current_user.longest_streak = current_user.current_streak
        
    current_user.last_active_date = now
    
    def award_badge(badge_name: str):
        badge = db.query(models.Badge).filter(models.Badge.name == badge_name).first()
        if badge:
            has_badge = db.query(models.UserBadge).filter(
                models.UserBadge.user_id == current_user.id, 
                models.UserBadge.badge_id == badge.id
            ).first()
            if not has_badge:
                user_badge = models.UserBadge(user_id=current_user.id, badge_id=badge.id)
                db.add(user_badge)

    award_badge("First Steps")
    if new_activity.steps and new_activity.steps >= 10000:
        award_badge("10k Club")
    if current_user.current_streak >= 3:
        award_badge("3-Day Streak")
    if current_user.current_streak >= 7:
        award_badge("7-Day Streak")

    db.commit()
    db.refresh(new_activity)
    return new_activity

@router.get("/export")
def export_activities(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    activities = db.query(models.Activity).filter(models.Activity.user_id == current_user.id).order_by(models.Activity.activity_date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Category", "Steps", "Duration (min)", "Notes"])
    
    for activity in activities:
        writer.writerow([
            activity.activity_date.strftime("%Y-%m-%d %H:%M:%S"),
            activity.category.capitalize(),
            activity.steps,
            activity.duration,
            activity.notes or ""
        ])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fitsteps_activities.csv"}
    )

@router.get("/", response_model=List[activity_schema.ActivityResponse])
def get_activities(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    activities = db.query(models.Activity).filter(models.Activity.user_id == current_user.id).all()
    return activities

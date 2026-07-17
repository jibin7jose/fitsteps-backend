from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from db import models
from schemas import activity as activity_schema
from api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=activity_schema.ActivityResponse)
def create_activity(activity: activity_schema.ActivityCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if activity.goal_id:
        goal = db.query(models.Goal).filter(models.Goal.id == activity.goal_id, models.Goal.user_id == current_user.id).first()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found or does not belong to user")
            
    new_activity = models.Activity(**activity.model_dump(), user_id=current_user.id)
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

@router.get("/", response_model=List[activity_schema.ActivityResponse])
def get_activities(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    activities = db.query(models.Activity).filter(models.Activity.user_id == current_user.id).all()
    return activities

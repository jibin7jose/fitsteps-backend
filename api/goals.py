from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from db import models
from schemas import goal as goal_schema
from api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=goal_schema.GoalResponse)
def create_goal(goal: goal_schema.GoalCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_goal = models.Goal(**goal.model_dump(), user_id=current_user.id)
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

@router.get("/", response_model=List[goal_schema.GoalResponse])
def get_goals(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    goals = db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()
    return goals

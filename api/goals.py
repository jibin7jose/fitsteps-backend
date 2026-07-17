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
    existing_goal = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id,
        models.Goal.goal_type == goal.goal_type,
        models.Goal.frequency == goal.frequency
    ).first()
    
    if existing_goal:
        existing_goal.target = goal.target
        db.commit()
        db.refresh(existing_goal)
        return existing_goal
    else:
        new_goal = models.Goal(**goal.model_dump(), user_id=current_user.id)
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        return new_goal

@router.get("/", response_model=List[goal_schema.GoalResponse])
def get_goals(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    goals = db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()
    return goals

@router.put("/{goal_id}", response_model=goal_schema.GoalResponse)
def update_goal(goal_id: int, goal_update: goal_schema.GoalUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id, models.Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if goal_update.target is not None:
        goal.target = goal_update.target
    if goal_update.frequency is not None:
        goal.frequency = goal_update.frequency
        
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id, models.Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully"}

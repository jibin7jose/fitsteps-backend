from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from schemas import gamification as gamification_schema
from api.dependencies import get_current_user
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.get("/summary", response_model=gamification_schema.GamificationSummary)
def get_gamification_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).options(
        joinedload(models.User.badges).joinedload(models.UserBadge.badge)
    ).filter(models.User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "last_active_date": user.last_active_date,
        "earned_badges": user.badges
    }

@router.post("/seed-badges")
def seed_default_badges(db: Session = Depends(get_db)):
    """Seed initial badges for the application."""
    badges_to_seed = [
        {"name": "First Steps", "description": "Logged your first activity", "icon_url": "🌱"},
        {"name": "10k Club", "description": "Logged over 10,000 steps in a single activity", "icon_url": "🔥"},
        {"name": "3-Day Streak", "description": "Logged activities for 3 consecutive days", "icon_url": "⚡"},
        {"name": "7-Day Streak", "description": "Logged activities for 7 consecutive days", "icon_url": "🏆"},
    ]
    
    added_badges = []
    for b in badges_to_seed:
        existing = db.query(models.Badge).filter(models.Badge.name == b["name"]).first()
        if not existing:
            new_badge = models.Badge(name=b["name"], description=b["description"], icon_url=b["icon_url"])
            db.add(new_badge)
            added_badges.append(b["name"])
            
    db.commit()
    return {"message": f"Seeded badges: {added_badges}"}

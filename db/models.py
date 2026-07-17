from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="USER")
    created_at = Column(DateTime, default=datetime.utcnow)

    goals = relationship("Goal", back_populates="owner", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="owner", cascade="all, delete-orphan")
    ai_recommendations = relationship("AIRecommendation", back_populates="owner", cascade="all, delete-orphan")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal_type = Column(String) # e.g., 'daily_steps', 'active_minutes'
    target = Column(Integer)
    frequency = Column(String) # e.g., 'daily', 'weekly'
    start_date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="goals")
    activities = relationship("Activity", back_populates="goal")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    category = Column(String) # e.g., 'walking', 'running', 'cycling'
    steps = Column(Integer, default=0)
    duration = Column(Integer, default=0) # in minutes
    activity_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

    owner = relationship("User", back_populates="activities")
    goal = relationship("Goal", back_populates="activities")

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recommended_steps = Column(Integer)
    reason = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="ai_recommendations")

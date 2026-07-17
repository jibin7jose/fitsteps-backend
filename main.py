from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, goals, activities, analytics, ai, gamification, leaderboard
from core.config import settings
from db.database import engine
from db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])
app.include_router(activities.router, prefix="/activities", tags=["activities"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
from api import gamification
app.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

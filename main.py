from fastapi import FastAPI
from api import auth, goals, activities, analytics, ai
from core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])
app.include_router(activities.router, prefix="/activities", tags=["activities"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

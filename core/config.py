import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FitSteps"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/fitsteps")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VeteranPath Lviv API"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "default_development_secret_key"
    
    # Захист: значення за замовчуванням завжди безпечне
    DATABASE_URL: str = "sqlite:///./veteranpath.db"
    
    # Google Gemini AI settings
    GEMINI_API_KEY: str = ""
    AI_MODE: str = "MOCK"  # 'GEMINI' or 'MOCK'
    
    # CORS settings
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Telegram Bot Settings
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_PARTNER_PASSWORD: str = "partner2025"
    TELEGRAM_ADMIN_PASSWORD: str = "admin2025"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

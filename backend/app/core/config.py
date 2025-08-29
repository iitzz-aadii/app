from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Dropout Prediction System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/dropout_db"
    DATABASE_TEST_URL: str = "postgresql://user:password@localhost/dropout_test_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ML Model
    MODEL_PATH: str = "app/ml/models/"
    MODEL_VERSION: str = "v1.0"

    # Risk Thresholds (configurable via admin panel)
    ATTENDANCE_SAFE_THRESHOLD: float = 75.0
    ATTENDANCE_WARNING_THRESHOLD: float = 60.0
    SCORE_SAFE_THRESHOLD: float = 60.0
    SCORE_WARNING_THRESHOLD: float = 40.0
    MAX_ATTEMPTS_THRESHOLD: int = 2

    # Notifications
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".csv", ".xlsx", ".xls"]

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    settings.DEBUG = True
    settings.DATABASE_URL = "postgresql://user:password@localhost/dropout_dev_db"

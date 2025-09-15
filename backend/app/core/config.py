from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/template_db"
    database_url_sync: str = "postgresql://postgres:postgres@db:5432/template_db"

    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    apple_client_id: Optional[str] = None
    apple_client_secret: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_team_id: Optional[str] = None

    # Email/Magic Link
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None

    # App
    app_name: str = "Vite React FastAPI Template"
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    # Environment
    environment: str = "development"
    debug: bool = True


settings = Settings()
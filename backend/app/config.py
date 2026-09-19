"""
Central application configuration.

All secrets are read from the .env file (never hard-coded).
Copy .env.example -> .env and fill in your own values.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/smarthire_ai"

    # JWT
    JWT_SECRET_KEY: str = "insecure-dev-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Bootstrap admin
    ADMIN_NAME: str = "System Administrator"
    ADMIN_EMAIL: str = "admin@smarthire.ai"
    ADMIN_PASSWORD: str = "Admin@12345"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached so the .env file is only parsed once per process."""
    return Settings()


settings = get_settings()

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Tickets"
    timezone: str = "America/Argentina/Buenos_Aires"
    debug: bool = False
    secret_key: str
    session_max_age_seconds: int = 60 * 60 * 12
    https_only_cookies: bool = True

    database_url: str

    admin_email: str
    admin_password: str
    admin_full_name: str = "Administrator"

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        """Railway exposes `postgresql://`; SQLAlchemy needs the psycopg 3 driver."""
        for prefix in ("postgresql://", "postgres://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value.removeprefix(prefix)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

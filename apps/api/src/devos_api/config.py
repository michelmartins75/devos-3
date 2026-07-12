from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "devos-api"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8080, alias="API_PORT")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )

    database_url: str = Field(
        default="postgresql+psycopg://devos_api:devos_api@localhost:5432/devos_app",
        alias="DATABASE_URL",
    )
    database_migrator_url: str = Field(
        default="postgresql+psycopg://devos_migrator:devos_migrator@localhost:5432/devos_app",
        alias="DATABASE_MIGRATOR_URL",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="TechKraft API", alias="APP_NAME")
    database_url: str = Field(
        default="sqlite:///./recruiter.db",
        alias="SQLALCHEMY_DATABASE_URL",
    )
    jwt_secret_key: str = Field(
        default="change-me-in-development",
        alias="JWT_SECRET_KEY",
    )
    access_token_expire_minutes: int = Field(
        default=15,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    cors_allowed_hosts: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://recruiter.local:8300",
        alias="CORS_ALLOWED_HOSTS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

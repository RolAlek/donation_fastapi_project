from pydantic import BaseModel, EmailStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    url: PostgresDsn


class UserSettings(BaseModel):
    secret: str
    lifetime: int = 3600
    superuser_login: EmailStr | None = None
    superuser_password: str | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="APP__",
        extra="allow",
        case_sensitive=False,
    )

    app_title: str = "Charity Project Application"
    db: DatabaseSettings
    user: UserSettings


settings = Settings()

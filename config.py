from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "changeme-insecure-default"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    database_url: str = "sqlite:///database.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

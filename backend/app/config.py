from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24 * 30
    invite_token_hours: int = 24 * 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

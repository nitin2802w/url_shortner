from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI URL Shortener"
    BASE_URL: str = "http://localhost:8000"
    DATABASE_URL: str
    REDIS_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Singleton settings instance used across the application
settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Logistics Data-Driven API (local)"
    APP_ENV: str = "local"
    APP_DEBUG: bool = True

    # DB (in future to Postgres/PostGIS)
    DB_DRIVER: str = "sqlite"
    SQLITE_URL: str = "sqlite:///./dev.db"

    class Config:
        env_file = ".env"

settings = Settings()
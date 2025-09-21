from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Logistics Data-Driven API"
    APP_ENV: str = "local"
    APP_DEBUG: bool = True

    # Database driver: "postgres" (using Alembic and psycopg2)
    DB_DRIVER: str = "postgres"

    # Postgres connection info (Docker compose defaults)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "logistics"
    POSTGRES_USER: str = "logistics"
    POSTGRES_PASSWORD: str = "root"

    class Config:
        env_file = ".env"

    # Helper to assemble SQLAlchemy URL
    @property
    def sqlalchemy_url(self) -> str:
        if self.DB_DRIVER == "postgres":
            return (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        raise ValueError("Unsupported DB_DRIVER")

settings = Settings()
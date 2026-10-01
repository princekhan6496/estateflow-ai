from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    FRONTEND_URL: str = "http://localhost:3000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def normalize_database_url(url: str) -> str:
    """Normalize the user-facing PostgreSQL URL for SQLAlchemy/psycopg v3."""
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


settings = Settings()
database_url = normalize_database_url(settings.DATABASE_URL)
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

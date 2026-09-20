import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def get_database_url():
    """
    Read the database URL from the environment.

    Render may provide PostgreSQL URLs using the legacy postgres:// scheme.
    SQLAlchemy expects postgresql://, so normalize it here.
    """
    database_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("DATABASE_URI")
    )

    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql://",
                1,
            )
        return database_url

    # Local development fallback.
    return f"sqlite:///{BASE_DIR / 'instance' / 'medisec.db'}"


def get_cors_origins():
    """
    Read comma-separated allowed origins.

    Example:
    CORS_ORIGINS=http://localhost:3000,https://medisec.vercel.app
    """
    configured_origins = os.getenv("CORS_ORIGINS", "")

    if configured_origins:
        return [
            origin.strip()
            for origin in configured_origins.split(",")
            if origin.strip()
        ]

    # Safe local-development defaults.
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ]


class Config:
    ENVIRONMENT = os.getenv(
        "FLASK_ENV",
        os.getenv("FLASK_CONFIG", "development"),
    )

    SECRET_KEY = os.getenv("SECRET_KEY")

    # Never silently use a predictable secret in production.
    if ENVIRONMENT == "production" and not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY must be configured when FLASK_ENV=production"
        )

    # Development-only fallback.
    if not SECRET_KEY:
        SECRET_KEY = "local-development-only-change-me"

    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # These options are valid for PostgreSQL and improve resilience when
    # Render closes idle connections.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    CORS_ORIGINS = get_cors_origins()

    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "False").lower()
        == "true"
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    PERMANENT_SESSION_LIFETIME = int(
        os.getenv("PERMANENT_SESSION_LIFETIME", "1800")
    )

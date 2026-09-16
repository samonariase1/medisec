import os

class Config:
    # Security: Do not run debug mode in production/demo
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1")
    
    # Database: Default to local SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///medisec.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # General Security
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_SAMESITE = "Lax"

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    DEBUG = False
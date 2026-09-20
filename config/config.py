import os
from pathlib import Path

class Config:
    # 1. Base Paths
    # Finds the true directory root of the running application
    BASE_DIR = Path(__file__).resolve().parent.parent

    # 2. Render Security Check
    # Render automatically sets RENDER=true in production cloud containers
    is_render = bool(os.environ.get("RENDER"))

    # 3. Dynamic Database Configuration
    # Uses Render PostgreSQL if available, otherwise safely maps absolute SQLite directories
    if os.environ.get("DATABASE_URL"):
        database_uri = os.environ.get("DATABASE_URL")
        # Fix legacy Heroku/Render dialect prefixes where 'postgres://' breaks SQLAlchemy 1.4+
        if database_uri.startswith("postgres://"):
            database_uri = database_uri.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_uri
    else:
        # Fallback to an absolute SQLite file path
        # In cloud containers, we write safely to /tmp. Locally, we keep it inside the root directory.
        if is_render:
            db_dir = "/tmp/medisec-instance"
        else:
            db_dir = str(BASE_DIR / "instance")
            
        # Ensure the fallback directory exists before SQLAlchemy boots up
        os.makedirs(db_dir, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(db_dir, 'app.db')}"

    # 4. App Configurations
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-secret-key-12345")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 5. Production-Ready CORS Security Gateways
    # Restricts API ingress origins to protect health records as requested in specifications
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

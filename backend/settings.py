import os

class Config:
    # Secret key for session management and security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'medisec-super-secret-hackathon-key'
    
    # SQLite database configuration (adjust if you are using PostgreSQL/MySQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:////tmp/medisec-instance/medisec.db'  # Replace /tmp/... when SQLlite db is created'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

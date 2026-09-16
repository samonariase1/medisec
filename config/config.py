import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'medisec-super-secret-hackathon-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///medisec.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# config.py
class Config:
    """Configuration settings for the Timetable Scheduling System."""
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/timetable.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
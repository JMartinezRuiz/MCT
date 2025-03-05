"""
Configuration settings for the application.
Different configurations for development, testing, and production environments.
"""
import os
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = Path(basedir).parent


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'  # Change in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(PROJECT_ROOT, 'mct.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload configuration
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads/documents')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'md', 'xlsx', 'xls', 'zip', 'rar', 'png', 'jpg', 'jpeg', 'gif'}


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Use stronger secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'strong-production-key'
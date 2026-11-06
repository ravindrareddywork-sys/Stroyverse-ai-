"""
StoryVerse AI — Configuration Module
=====================================
Loads environment variables and provides configuration
classes for different environments (development, testing, production).

Simple explanation: This file is like the "settings panel" of the application.
Instead of hardcoding values like the database path or secret key inside the
code, we read them from environment variables. This keeps sensitive data safe.
"""

import os
from dotenv import load_dotenv

# Explicitly load .env file from the backend directory (or fallback to CWD)
basedir = os.path.abspath(os.path.dirname(__file__))
env_file = os.path.join(basedir, ".env")
if os.path.exists(env_file):
    load_dotenv(env_file, override=True)
else:
    load_dotenv()


class Config:
    """
    Base configuration shared across all environments.
    All sensitive values come from environment variables.
    """

    # --- Flask Core ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    TESTING = False

    # --- Database ---
    # SQLite database stored in backend/instance/ folder
    # Flask automatically creates the instance/ folder
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///storyverse.db"
    )
    # Disable modification tracking to save memory (we don't need it)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- AI Provider ---
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini")
    AI_MOCK_MODE = os.environ.get("AI_MOCK_MODE", "false").lower() in ("true", "1", "yes")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    AI_REQUEST_TIMEOUT = int(os.environ.get("AI_REQUEST_TIMEOUT", 30))

    # --- CORS ---
    # Which frontend origins are allowed to call our API
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000,http://localhost:5000,http://127.0.0.1:5000"
    ).split(",")

    # --- Rate Limiting ---
    RATELIMIT_DEFAULT = os.environ.get("RATE_LIMIT_DEFAULT", "2000 per day, 500 per hour")
    RATELIMIT_GENERATION = os.environ.get("RATE_LIMIT_GENERATION", "10 per minute")
    RATELIMIT_STORAGE_URI = "memory://"  # Store rate limit data in memory for dev

    # --- Input / Output Limits ---
    MAX_INPUT_LENGTH = int(os.environ.get("MAX_INPUT_LENGTH", 2000))
    MAX_OUTPUT_LENGTH = int(os.environ.get("MAX_OUTPUT_LENGTH", 50000))
    MAX_EXPORT_SIZE = int(os.environ.get("MAX_EXPORT_SIZE", 5242880))  # 5 MB

    # --- Paths ---
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    GENERATED_FILES_DIR = os.path.join(BASE_DIR, "generated_files")

    # --- RAG (Retrieval-Augmented Generation) & ChromaDB ---
    RAG_ENABLED = os.environ.get("RAG_ENABLED", "true").lower() in ("true", "1", "yes")
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    CHROMA_PERSIST_DIRECTORY = os.environ.get(
        "CHROMA_PERSIST_DIRECTORY", os.path.join(BASE_DIR, "instance", "chroma_db")
    )
    RAG_COLLECTION_NAME = os.environ.get("RAG_COLLECTION_NAME", "storyverse_knowledge_base")
    RAG_DEFAULT_TOP_K = int(os.environ.get("RAG_DEFAULT_TOP_K", 3))



class DevelopmentConfig(Config):
    """
    Development configuration.
    Debug mode is ON so Flask shows detailed error messages in the terminal.
    Never use DEBUG=True in production.
    """
    DEBUG = True
    FLASK_ENV = "development"


class TestingConfig(Config):
    """
    Testing configuration.
    Uses an in-memory SQLite database so tests don't touch the real database.
    TESTING=True makes Flask propagate exceptions instead of handling them
    (useful for pytest to catch them properly).
    """
    TESTING = True
    DEBUG = True
    # In-memory database: fast, isolated, destroyed after tests complete
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disable rate limiting during tests
    RATELIMIT_ENABLED = False
    # AI mock mode for fast and quota-free automated testing
    AI_MOCK_MODE = True
    AI_PROVIDER = "mock"
    # Disable CSRF protection if added later
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Production configuration.
    Debug mode is OFF. Uses environment-configured database and secret key.
    """
    DEBUG = False
    TESTING = False
    FLASK_ENV = "production"

    # In production, ensure secret key is loaded from environment
    SECRET_KEY = os.environ.get("SECRET_KEY", "storyverse-production-fallback-key-please-set-env")

    # In production, normalize postgres:// to postgresql:// for modern SQLAlchemy compatibility
    db_url = os.environ.get("DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url


# Configuration registry — maps environment name to class
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(config_name: str = None):
    """
    Returns the appropriate configuration class.

    Args:
        config_name: "development", "testing", or "production".
                     Falls back to the FLASK_ENV environment variable,
                     then defaults to "development".
    """
    env = (config_name or os.environ.get("FLASK_ENV", "development")).lower()
    return config_map.get(env, DevelopmentConfig)

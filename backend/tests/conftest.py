"""
StoryVerse AI — Test Configuration (conftest.py)
==================================================
pytest loads this file automatically before running any tests.

What this file does:
  1. Builds a Flask app wired to a temporary IN-MEMORY SQLite database
     so tests NEVER touch the real development database.
  2. Provides a "client" fixture — a fake browser that can send HTTP
     requests to the app without actually starting a server.
  3. Provides a "db_session" fixture for direct database operations in tests.

Fixtures are reusable helpers that pytest injects into test functions
automatically whenever a test declares them as parameters.
"""

import os
import pytest

# Ensure testing environment uses mock AI mode by default
os.environ["AI_MOCK_MODE"] = "true"
os.environ["AI_PROVIDER"] = "mock"

from app import create_app
from extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """
    Session-scoped fixture: creates one Flask app for the entire test run.
    Uses the "testing" config which points SQLAlchemy at an in-memory database.
    """
    flask_app = create_app("testing")

    # Provide application context so db operations work inside tests
    with flask_app.app_context():
        _db.create_all()          # Create all tables in the in-memory DB
        yield flask_app           # Hand the app to the test
        _db.drop_all()            # Clean up after all tests finish


@pytest.fixture(scope="function")
def client(app):
    """
    Function-scoped fixture: provides a fresh test client for each test.
    The test client lets us call app.get("/api/health") without a real server.
    """
    with app.test_client() as testing_client:
        yield testing_client


@pytest.fixture(scope="function")
def db_session(app):
    """
    Function-scoped fixture: provides a database session for direct DB operations.
    Rolls back any changes after each test so tests don't affect each other.
    """
    with app.app_context():
        yield _db.session
        _db.session.rollback()

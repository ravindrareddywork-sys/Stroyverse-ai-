"""
StoryVerse AI — Extensions Module
===================================
Initializes Flask extensions WITHOUT binding them to a specific Flask app.
This is the standard pattern called "Application Factory Pattern".

Simple explanation:
  Normally you'd write: db = SQLAlchemy(app)
  But that ties the database to one specific app object, making testing hard.
  Instead we write: db = SQLAlchemy()
  And later call: db.init_app(app)
  This lets us create different app instances for testing vs production.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- SQLAlchemy Database Extension ---
# This handles all database operations.
# We create it here and bind it to the app in app.py
db = SQLAlchemy()

# --- CORS Extension ---
# Allows the frontend (running on port 3000) to call
# the backend API (running on port 5000).
# Without this, browsers block cross-origin requests.
cors = CORS()

# --- Rate Limiter Extension ---
# Prevents abuse by limiting how many requests
# a single IP address can make per minute/hour.
# get_remote_address extracts the client's IP address automatically.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
)

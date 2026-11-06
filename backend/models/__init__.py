"""
StoryVerse AI — Models Package Init
======================================
Imports all models so SQLAlchemy can discover them when
db.create_all() is called in app.py.

Important: Both models MUST be imported here, otherwise
SQLAlchemy won't know they exist and won't create their tables.
"""

from .project import Project
from .generation_history import GenerationHistory

__all__ = ["Project", "GenerationHistory"]

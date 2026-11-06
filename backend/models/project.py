"""
StoryVerse AI — Project Model
================================
Represents a saved creative writing project.
Each project stores the generated story or script along with
all the parameters used to generate it.

Simple explanation:
  Think of a Project like a saved document in Microsoft Word.
  It has a title, content, and information about when it was created.
  One project can have many "history records" showing every AI generation attempt.
"""

from datetime import datetime, timezone
from extensions import db


class Project(db.Model):
    """
    SQLAlchemy model for a user's creative writing project.

    Table name: project
    """

    __tablename__ = "project"

    # --- Primary Key ---
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # --- Project Identity ---
    title = db.Column(db.String(500), nullable=False)
    # content_type distinguishes stories from scripts
    # Allowed values: 'story', 'script', 'character'
    content_type = db.Column(db.String(50), nullable=False, default="story")

    # --- Generation Parameters (what the user chose) ---
    genre = db.Column(db.String(100), nullable=True)
    language = db.Column(db.String(50), nullable=True, default="English")
    tone = db.Column(db.String(50), nullable=True)
    topic = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)

    # --- Generated Content ---
    # The full AI-generated story, script or character profile
    generated_content = db.Column(db.Text, nullable=True)

    # --- Timestamps (always stored in UTC) ---
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationship to GenerationHistory ---
    # One project → many history records
    # cascade="all, delete-orphan" means: when a project is deleted,
    # all its history records are automatically deleted too.
    history = db.relationship(
        "GenerationHistory",
        backref="project",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="GenerationHistory.created_at.desc()",
    )

    def to_dict(self, include_history=False):
        """
        Converts the model instance to a plain Python dictionary.
        This is used when sending data as JSON to the frontend.

        Args:
            include_history: If True, includes generation history records.

        Returns:
            dict: Project data as a JSON-serializable dictionary.
        """
        data = {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "project_type": self.content_type,
            "genre": self.genre,
            "language": self.language,
            "tone": self.tone,
            "topic": self.topic,
            "description": self.description or self.topic,
            "generated_content": self.generated_content,
            "content": self.generated_content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_history:
            data["history"] = [h.to_dict() for h in self.history]
        return data

    def update_from_dict(self, data):
        """
        Updates model fields from a dictionary.
        Only updates fields that are present in the dictionary.
        Automatically sets updated_at to the current UTC time.

        Args:
            data: Dictionary of field names and new values.
        """
        allowed_fields = [
            "title", "content_type", "genre", "language",
            "tone", "topic", "description", "generated_content"
        ]
        # Map aliases
        if "project_type" in data and "content_type" not in data:
            self.content_type = data["project_type"]
        if "content" in data and "generated_content" not in data:
            self.generated_content = data["content"]
        if "description" in data and "topic" not in data and not self.topic:
            self.topic = data["description"]
        if "topic" in data and "description" not in data and not self.description:
            self.description = data["topic"]

        for field in allowed_fields:
            if field in data and hasattr(self, field):
                setattr(self, field, data[field])
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self):
        """String representation for debugging."""
        return f"<Project id={self.id} title='{self.title}' type='{self.content_type}'>"

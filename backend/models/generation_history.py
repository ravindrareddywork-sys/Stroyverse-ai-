"""
StoryVerse AI — GenerationHistory Model
==========================================
Records every AI generation attempt for a project.
This creates a "history trail" so users can see previous versions.

Simple explanation:
  Every time the AI generates content (original generation, rewrite,
  expand, shorten, etc.), we save a record. This is like the "version
  history" in Google Docs — you can see what was generated before.
"""

from datetime import datetime, timezone
from extensions import db


class GenerationHistory(db.Model):
    """
    SQLAlchemy model for a single AI generation event.

    Relationship: Many GenerationHistory records belong to ONE Project.
    Table name: generation_history
    """

    __tablename__ = "generation_history"

    # --- Primary Key ---
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # --- Foreign Key linking to Project ---
    # nullable=False means every history record MUST belong to a project.
    # ondelete="CASCADE" ensures the DB removes orphan rows automatically.
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Index for faster lookups by project_id
    )

    # --- What operation was performed ---
    # Examples: 'generate', 'regenerate', 'expand', 'shorten',
    #           'continue', 'translate', 'rewrite', etc.
    operation = db.Column(db.String(100), nullable=False, default="generate")

    # --- Content type involved ---
    # 'story', 'script', or 'character'
    content_type = db.Column(db.String(50), nullable=True)

    # --- Snapshot of the generated content ---
    # Stored so users can review past versions
    content_snapshot = db.Column(db.Text, nullable=True)

    # --- Summary of the inputs that produced this generation ---
    # e.g. "Topic: space heist, Genre: Thriller, Language: English"
    input_summary = db.Column(db.String(500), nullable=True)

    # --- What was sent to the AI ---
    prompt = db.Column(db.Text, nullable=True)

    # --- AI metadata ---
    ai_model = db.Column(db.String(100), nullable=True)
    tokens_used = db.Column(db.Integer, nullable=True)

    # --- Timestamp (UTC) ---
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """
        Converts the history record to a plain dictionary for JSON responses.

        Returns:
            dict: History data as a JSON-serializable dictionary.
        """
        return {
            "id": self.id,
            "project_id": self.project_id,
            "operation": self.operation,
            "content_type": self.content_type,
            "content_snapshot": self.content_snapshot,
            "input_summary": self.input_summary,
            "prompt": self.prompt,
            "ai_model": self.ai_model,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        """String representation for debugging."""
        return (
            f"<GenerationHistory id={self.id} "
            f"project_id={self.project_id} "
            f"operation='{self.operation}'>"
        )

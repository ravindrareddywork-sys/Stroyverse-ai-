"""
StoryVerse AI — Routes Package Init
=======================================
Registers all Flask Blueprints with the application.
A Blueprint is Flask's way of organizing routes into separate modules.

Simple explanation:
  Instead of putting ALL routes in one file (which would be huge),
  we split them into separate files. Each file is a "Blueprint".
  This function connects all the blueprints to the main Flask app.
"""

from .health_routes import health_bp


def register_blueprints(app):
    """
    Registers all Flask Blueprints on the application.
    Called once during app creation in app.py.

    As new features are added in later phases, more blueprints
    will be imported and registered here.

    Args:
        app: The Flask application instance.
    """
    # Phase 2: Health endpoint
    app.register_blueprint(health_bp, url_prefix="/api")

    # Phase 5: Story generation
    from .story_routes import story_bp
    app.register_blueprint(story_bp, url_prefix="/api")

    # Phase 6: Script generation
    from .script_routes import script_bp
    app.register_blueprint(script_bp, url_prefix="/api")

    # Phase 7: Character generation
    from .character_routes import character_bp
    app.register_blueprint(character_bp, url_prefix="/api")

    # Phase 8: AI writing assistant
    from .writing_assistant_routes import writing_assistant_bp
    app.register_blueprint(writing_assistant_bp, url_prefix="/api")

    # Phase 9: Project management
    from .project_routes import project_bp
    app.register_blueprint(project_bp, url_prefix="/api")

    # Phase 10: Document export
    from .export_routes import export_bp
    app.register_blueprint(export_bp, url_prefix="/api")

    # Phase RAG: Retrieval-Augmented Generation
    from .rag_routes import rag_bp
    app.register_blueprint(rag_bp, url_prefix="/api")

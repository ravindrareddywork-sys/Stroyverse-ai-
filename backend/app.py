"""
StoryVerse AI — Flask Application Factory
===========================================
This is the MAIN entry point for the backend server.

What is an Application Factory?
  Instead of creating the Flask app as a global variable (which causes
  problems during testing), we create it inside a function called
  create_app(). This way, tests can call create_app("testing") and get
  a fresh app with a temporary test database — no contamination of real data.

How Flask starts:
  1. Python calls create_app() to build the app object.
  2. Config is loaded (dev / test / prod).
  3. Extensions (database, CORS, rate limiter) are attached.
  4. Database tables are created if they don't exist.
  5. All route blueprints are registered.
  6. Error handlers are registered.
  7. The app is returned and started with app.run().
"""

import logging
import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from config import get_config
from extensions import db, cors, limiter
from utils.error_handler import register_error_handlers


def create_app(config_name: str = None) -> Flask:
    """
    Application factory — creates and configures the Flask application.

    Args:
        config_name: One of "development", "testing", "production".
                     Defaults to the FLASK_ENV environment variable
                     or "development" if not set.

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    # Support reverse proxies/tunnels (localtunnel, ngrok, etc.) so X-Forwarded-For gives accurate client IPs
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # ------------------------------------------------------------------ #
    # 1. Load Configuration                                                #
    # ------------------------------------------------------------------ #
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app.config.from_object(get_config(config_name))

    # Ensure the instance and generated_files folders exist on disk
    os.makedirs(app.instance_path, exist_ok=True)
    generated_dir = os.path.join(os.path.dirname(__file__), "generated_files")
    os.makedirs(generated_dir, exist_ok=True)

    # ------------------------------------------------------------------ #
    # 2. Set up Logging                                                    #
    # ------------------------------------------------------------------ #
    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting StoryVerse AI in '{config_name}' mode")

    # ------------------------------------------------------------------ #
    # 3. Initialize Extensions                                             #
    # ------------------------------------------------------------------ #
    db.init_app(app)
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("CORS_ORIGINS", ["http://localhost:5500", "http://127.0.0.1:5500"]),
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
        supports_credentials=False,
    )
    limiter.init_app(app)

    # ------------------------------------------------------------------ #
    # 4. Create Database Tables                                            #
    # ------------------------------------------------------------------ #
    with app.app_context():
        # Import models so SQLAlchemy knows about them before create_all()
        from models import Project, GenerationHistory  # noqa: F401

        db.create_all()

        # Safe schema migration for existing SQLite databases (Phase 9)
        try:
            from sqlalchemy import text
            cols = [
                row[1] for row in db.session.execute(text("PRAGMA table_info(project)")).fetchall()
            ]
            if cols and "description" not in cols:
                db.session.execute(text("ALTER TABLE project ADD COLUMN description TEXT"))
                db.session.commit()
                logger.info("Migrated schema: added description column to project table.")
        except Exception as mig_err:
            logger.debug(f"Schema check completed: {mig_err}")

        logger.info("Database tables created / verified.")

    # ------------------------------------------------------------------ #
    # 5. Register Blueprints (Routes)                                      #
    # ------------------------------------------------------------------ #
    from routes import register_blueprints

    register_blueprints(app)
    logger.info("All route blueprints registered.")

    # ------------------------------------------------------------------ #
    # 6. Serve Frontend (SPA & Static Pages)                               #
    # ------------------------------------------------------------------ #
    from flask import send_from_directory
    from utils.response import not_found_response

    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    @limiter.exempt
    def serve_frontend(path):
        if path == "api" or path.startswith("api/"):
            return not_found_response("API endpoint not found.")
        target = os.path.join(frontend_dir, path)
        if os.path.isfile(target):
            return send_from_directory(frontend_dir, path)
        index_target = os.path.join(frontend_dir, "index.html")
        if os.path.isfile(index_target):
            return send_from_directory(frontend_dir, "index.html")
        return ("Frontend not found", 404)

    # ------------------------------------------------------------------ #
    # 7. Register Error Handlers                                           #
    # ------------------------------------------------------------------ #
    register_error_handlers(app)

    return app


# ------------------------------------------------------------------ #
# Entry point — run with:  python app.py                             #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    print(f"\n{'='*55}")
    print(f"  StoryVerse AI Backend")
    print(f"  Running at: http://127.0.0.1:{port}")
    print(f"  Health:     http://127.0.0.1:{port}/api/health")
    print(f"  Debug mode: {debug}")
    print(f"{'='*55}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)

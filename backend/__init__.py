import logging
import os
from flask import Flask
from .config import Config
from .extensions import limiter, cors


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"),
        static_url_path="/",
    )

    # Load configuration
    app.config.from_object(Config())

    # Initialize extensions
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    limiter.init_app(app)

    # Logging
    _configure_logging(app)

    # Blueprints
    from .routes.api import api_bp
    from .routes.pages import pages_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(pages_bp)

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok", "ai_enabled": app.config.get("AI_ENABLED", False)}

    return app


def _configure_logging(app: Flask) -> None:
    level = logging.INFO
    if app.debug or app.testing:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    # Reduce noisy loggers
    logging.getLogger("google").setLevel(logging.WARNING)


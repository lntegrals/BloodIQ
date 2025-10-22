import os
from flask import Blueprint, current_app, send_from_directory


pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def index():
    # Serve SPA index.html from frontend/dist if present, else a simple placeholder
    dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
    index_path = os.path.join(dist, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(dist, "index.html")
    return {
        "message": "BloodLens 2.0 – Frontend not built yet. Use /api endpoints or run frontend dev server.",
        "api": ["/api/results", "/api/advice/<type>"]
    }


# Fallback for SPA routes like /results
@pages_bp.get("/results")
def spa_results():
    return index()


"""
app.py
------
Flask application entry point (application/API layer).

Run locally with:
    python backend/app.py

This wires together:
  - Cloud database service (cloud/database_service.py)
  - Cloud storage service (cloud/storage_service.py)
  - AI diet engine (ai_engine/diet_engine.py)
  - REST route blueprints (backend/routes/*)
"""

import os
import sys
from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Allow running this file directly (python backend/app.py) by ensuring the
# project root is on sys.path so `cloud` and `ai_engine` imports resolve.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import Config
from cloud.database_service import init_db
from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.plan_routes import plan_bp
from backend.routes.file_routes import file_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        minutes=Config.JWT_ACCESS_TOKEN_EXPIRES_MINUTES
    )

    # CORS: only allow the configured frontend origin (a basic cloud-security practice)
    CORS(app, resources={r"/*": {"origins": Config.FRONTEND_ORIGIN}}, supports_credentials=True)

    JWTManager(app)

    init_db()  # "provision" tables -- equivalent to setting up cloud DB collections

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(file_bp)

    @app.get("/")
    def health_check():
        return jsonify({
            "status": "ok",
            "service": "AI-Powered Personal Diet Planner API",
            "message": "Backend is running. See /docs or README.md for API reference.",
        }), 200

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "resource not found"}), 404

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)

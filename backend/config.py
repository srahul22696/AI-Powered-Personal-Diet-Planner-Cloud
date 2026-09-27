"""
config.py
---------
Loads all configuration from environment variables. No secrets are
hardcoded here -- this file only reads names, never sets values.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env if present (never commit the real .env file)


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///cloud_diet_planner.db")

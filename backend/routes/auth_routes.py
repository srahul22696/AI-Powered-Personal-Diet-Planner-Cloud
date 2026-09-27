"""
auth_routes.py
--------------
POST /register
POST /login
POST /logout

Authentication concept: on login we issue a JWT access token. The client
stores it (e.g. in memory / localStorage) and sends it as
`Authorization: Bearer <token>` on every subsequent request. The server
never needs to store session state -> this is what makes the API
"stateless" and horizontally scalable (a core cloud-computing property).
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from cloud import database_service as db
from backend.utils.security import (
    hash_password, verify_password, is_valid_email, is_valid_password
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name:
        return jsonify({"error": "name is required"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "a valid email is required"}), 400
    if not is_valid_password(password):
        return jsonify({"error": "password must be at least 8 characters"}), 400

    if db.get_user_by_email(email):
        return jsonify({"error": "an account with this email already exists"}), 409

    user_id = db.create_user(name, email, hash_password(password))
    token = create_access_token(identity=user_id)

    return jsonify({
        "message": "registration successful",
        "access_token": token,
        "user": {"user_id": user_id, "name": name, "email": email},
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db.get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        # Deliberately vague error -- do not reveal whether email exists.
        return jsonify({"error": "invalid email or password"}), 401

    token = create_access_token(identity=user["user_id"])
    return jsonify({
        "message": "login successful",
        "access_token": token,
        "user": {"user_id": user["user_id"], "name": user["name"], "email": user["email"]},
    }), 200


@auth_bp.post("/logout")
def logout():
    # JWTs are stateless; "logout" is handled client-side by discarding the
    # token. In a production system you might additionally maintain a
    # short-lived token blocklist -- noted here for interview completeness.
    return jsonify({"message": "logged out (discard token client-side)"}), 200

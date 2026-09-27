"""
profile_routes.py
------------------
GET /profile
PUT /profile

User isolation concept: get_jwt_identity() gives us the user_id embedded in
the caller's OWN token. Every query is scoped to that id, so User A can
never read or modify User B's profile, even if they guess an id.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from cloud import database_service as db
from backend.utils.security import validate_profile_fields

profile_bp = Blueprint("profile", __name__)


def _public_profile(user: dict) -> dict:
    import json
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "age": user["age"],
        "height_cm": user["height_cm"],
        "weight_kg": user["weight_kg"],
        "activity_level": user["activity_level"],
        "dietary_preference": user["dietary_preference"],
        "goal": user["goal"],
        "allergies": json.loads(user["allergies"] or "[]"),
        "created_at": user["created_at"],
    }


@profile_bp.get("/profile")
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify(_public_profile(user)), 200


@profile_bp.put("/profile")
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    errors = validate_profile_fields(data)
    if errors:
        return jsonify({"error": "validation failed", "details": errors}), 400

    updated = db.update_profile(user_id, data)
    if not updated:
        return jsonify({"error": "user not found"}), 404
    return jsonify(_public_profile(updated)), 200

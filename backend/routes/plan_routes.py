"""
plan_routes.py
--------------
POST   /generate-plan
GET    /plans
GET    /plans/<plan_id>
DELETE /plans/<plan_id>

Demonstrates: API layer -> AI engine -> Cloud database, plus strict
per-user data isolation on every read/delete.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from cloud import database_service as db
from ai_engine import diet_engine

plan_bp = Blueprint("plan", __name__)


@plan_bp.post("/generate-plan")
@jwt_required()
def generate_plan_route():
    user_id = get_jwt_identity()
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    data = request.get_json(silent=True) or {}
    dietary_preference = data.get("dietary_preference") or user.get("dietary_preference") or "vegetarian"
    goal = data.get("goal") or user.get("goal") or "maintenance"

    import json
    allergies = json.loads(user["allergies"] or "[]")

    target_calories = None
    if user.get("age") and user.get("height_cm") and user.get("weight_kg"):
        targets = diet_engine.compute_daily_targets(
            age=user["age"], height_cm=user["height_cm"], weight_kg=user["weight_kg"],
            activity_level=user.get("activity_level") or "sedentary", goal=goal,
        )
        target_calories = targets["target_calories"]

    result = diet_engine.generate_plan(
        dietary_preference=dietary_preference,
        goal=goal,
        allergies=allergies,
        target_calories=target_calories,
    )

    plan = db.create_plan(
        user_id=user_id,
        breakfast=result["breakfast"],
        lunch=result["lunch"],
        snack=result["snack"],
        dinner=result["dinner"],
        nutrition_summary=result["nutrition_summary"],
        source=result["source"],
    )
    plan["disclaimer"] = result.get("disclaimer")
    if target_calories:
        plan["target_calories"] = target_calories

    return jsonify(plan), 201


@plan_bp.get("/plans")
@jwt_required()
def list_plans_route():
    user_id = get_jwt_identity()
    return jsonify(db.list_plans(user_id)), 200


@plan_bp.get("/plans/<plan_id>")
@jwt_required()
def get_plan_route(plan_id):
    user_id = get_jwt_identity()
    plan = db.get_plan(user_id, plan_id)
    if not plan:
        # Note: returns 404 (not 403) for a plan owned by someone else too,
        # so we don't leak information about which plan_ids exist.
        return jsonify({"error": "plan not found"}), 404
    return jsonify(plan), 200


@plan_bp.delete("/plans/<plan_id>")
@jwt_required()
def delete_plan_route(plan_id):
    user_id = get_jwt_identity()
    deleted = db.delete_plan(user_id, plan_id)
    if not deleted:
        return jsonify({"error": "plan not found"}), 404
    return jsonify({"message": "plan deleted"}), 200

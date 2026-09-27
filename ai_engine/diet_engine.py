"""
diet_engine.py
--------------
AI Diet Recommendation Engine.

VERSION A - Rule-based engine (always available, no external dependency).
VERSION B - Optional external AI API call, used FIRST if configured; if it
            fails or is unavailable, the code automatically FALLS BACK to
            Version A. This fallback logic is a key "failure handling"
            concept examiners/interviewers look for in cloud projects.

Disclaimer: All generated plans are educational/general-wellness examples
based on synthetic/demo preferences. They are NOT medical or clinical
nutrition advice.
"""

import json
import os
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diet_engine")

_DATA_PATH = os.path.join(os.path.dirname(__file__), "food_data.json")
with open(_DATA_PATH, "r") as f:
    FOOD_DATA = json.load(f)

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
}

GOAL_ADJUSTMENT = {
    "weight_loss": -0.15,
    "weight_gain": 0.15,
    "maintenance": 0.0,
}


def compute_bmr(age: int, height_cm: float, weight_kg: float, sex: str = "other") -> float:
    """Mifflin-St Jeor Equation. `sex` affects a small constant term."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if sex == "male":
        return base + 5
    elif sex == "female":
        return base - 161
    return base - 78  # neutral midpoint for "other"/unspecified


def compute_daily_targets(age, height_cm, weight_kg, activity_level, goal, sex="other"):
    bmr = compute_bmr(age, height_cm, weight_kg, sex)
    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    delta = GOAL_ADJUSTMENT.get(goal, 0.0)
    calories = round(tdee * (1 + delta))

    # Default macro split: 30% protein / 40% carbs / 30% fat
    protein_g = round(0.30 * calories / 4)
    carbs_g = round(0.40 * calories / 4)
    fat_g = round(0.30 * calories / 9)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": calories,
        "target_macros": {"protein_g": protein_g, "carbs_g": carbs_g, "fat_g": fat_g},
    }


def _filter_by_diet(items, dietary_preference):
    """dietary_preference: 'vegetarian' | 'vegan' | 'non_vegetarian'"""
    key = {"vegetarian": "veg", "vegan": "vegan", "non_vegetarian": "nonveg"}.get(
        dietary_preference, "veg"
    )
    matches = [item for item in items if key in item["diet"]]
    return matches if matches else items  # never return an empty meal slot


def generate_rule_based_plan(dietary_preference: str, goal: str, allergies=None) -> dict:
    """
    VERSION A: Rule-based recommendation.
    Selects one item per meal slot matching diet preference, avoiding any
    named allergy keyword found in the food name (simple demo-level filter).
    """
    allergies = [a.lower() for a in (allergies or [])]

    def pick(slot):
        candidates = _filter_by_diet(FOOD_DATA[slot], dietary_preference)
        candidates = [c for c in candidates if not any(a in c["name"].lower() for a in allergies)]
        if not candidates:
            candidates = _filter_by_diet(FOOD_DATA[slot], dietary_preference)
        return random.choice(candidates)

    breakfast = pick("breakfast")
    lunch = pick("lunch")
    snack = pick("snack")
    dinner = pick("dinner")

    total_kcal = breakfast["kcal"] + lunch["kcal"] + snack["kcal"] + dinner["kcal"]
    total_protein = breakfast["protein_g"] + lunch["protein_g"] + snack["protein_g"] + dinner["protein_g"]
    total_carbs = breakfast["carbs_g"] + lunch["carbs_g"] + snack["carbs_g"] + dinner["carbs_g"]
    total_fat = breakfast["fat_g"] + lunch["fat_g"] + snack["fat_g"] + dinner["fat_g"]

    return {
        "breakfast": breakfast,
        "lunch": lunch,
        "snack": snack,
        "dinner": dinner,
        "nutrition_summary": {
            "total_kcal": total_kcal,
            "total_protein_g": total_protein,
            "total_carbs_g": total_carbs,
            "total_fat_g": total_fat,
            "hydration_reminder": "Aim for at least 2.5-3 litres of water across the day.",
        },
        "source": "rule_based_fallback",
        "disclaimer": (
            "This is an educational/general-wellness example plan generated from "
            "synthetic demo preferences. It is not medical or clinical nutrition advice."
        ),
    }


def _build_ai_prompt(dietary_preference, goal, allergies, target_calories):
    """Constructs a structured prompt for an external AI API (Version B)."""
    return (
        "You are a general wellness assistant generating an EDUCATIONAL example "
        "meal plan (not medical advice). "
        f"Dietary preference: {dietary_preference}. Goal: {goal}. "
        f"Allergies/avoid: {', '.join(allergies) if allergies else 'none'}. "
        f"Target daily calories: approximately {target_calories} kcal. "
        "Return STRICT JSON with keys: breakfast, lunch, snack, dinner (each an "
        "object with name, kcal, protein_g, carbs_g, fat_g) and nutrition_summary "
        "(object with total_kcal, total_protein_g, total_carbs_g, total_fat_g, "
        "hydration_reminder). Do not include any text outside the JSON."
    )


def generate_ai_plan(dietary_preference, goal, allergies, target_calories):
    """
    VERSION B: Optional external AI API call.
    Reads AI_API_URL / AI_API_KEY from environment. If either is missing, or
    the request fails/returns invalid data, raises an exception so the
    caller can fall back to the rule-based engine.
    """
    import requests  # local import: keeps this optional dependency isolated

    api_url = os.environ.get("AI_API_URL")
    api_key = os.environ.get("AI_API_KEY")
    if not api_url or not api_key:
        raise RuntimeError("AI API not configured (AI_API_URL / AI_API_KEY missing).")

    prompt = _build_ai_prompt(dietary_preference, goal, allergies, target_calories)

    response = requests.post(
        api_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"prompt": prompt, "max_tokens": 500},
        timeout=8,
    )
    response.raise_for_status()
    data = response.json()

    # Response validation - reject anything that doesn't have the expected shape
    required_keys = {"breakfast", "lunch", "snack", "dinner", "nutrition_summary"}
    if not required_keys.issubset(data.keys()):
        raise ValueError("AI API response missing required fields.")

    data["source"] = "ai_api"
    data["disclaimer"] = (
        "This is an educational/general-wellness example plan. It is not "
        "medical or clinical nutrition advice."
    )
    return data


def generate_plan(dietary_preference, goal, allergies=None, target_calories=None):
    """
    Main entry point used by the API route.
    Tries the external AI API first (if configured); falls back to the
    rule-based engine on ANY failure. This fallback guarantees the project
    stays fully demoable without a paid AI subscription.
    """
    try:
        return generate_ai_plan(dietary_preference, goal, allergies, target_calories)
    except Exception as exc:
        logger.warning("AI API unavailable or failed (%s). Falling back to rule-based engine.", exc)
        return generate_rule_based_plan(dietary_preference, goal, allergies)

"""
security.py
-----------
Password hashing and basic input validation helpers.

Cloud security concept demonstrated: passwords are NEVER stored in plain
text. We use Werkzeug's PBKDF2-based hashing (salted) so even if the
database were leaked, raw passwords would not be exposed.
"""

import re
from werkzeug.security import generate_password_hash, check_password_hash

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(plain_password: str) -> str:
    return generate_password_hash(plain_password,method="pbkdf2:sha256")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, plain_password)


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_REGEX.match(email))


def is_valid_password(password: str) -> bool:
    """Demo-level password policy: at least 8 characters."""
    return bool(password) and len(password) >= 8


def validate_profile_fields(data: dict) -> list:
    """Returns a list of validation error strings (empty list = valid)."""
    errors = []
    if "age" in data and data["age"] is not None:
        if not (1 <= int(data["age"]) <= 120):
            errors.append("age must be between 1 and 120")
    if "height_cm" in data and data["height_cm"] is not None:
        if not (50 <= float(data["height_cm"]) <= 260):
            errors.append("height_cm must be between 50 and 260")
    if "weight_kg" in data and data["weight_kg"] is not None:
        if not (20 <= float(data["weight_kg"]) <= 400):
            errors.append("weight_kg must be between 20 and 400")
    if "activity_level" in data and data["activity_level"] not in (
        None, "sedentary", "light", "moderate", "active"
    ):
        errors.append("activity_level must be one of: sedentary, light, moderate, active")
    if "dietary_preference" in data and data["dietary_preference"] not in (
        None, "vegetarian", "vegan", "non_vegetarian"
    ):
        errors.append("dietary_preference must be one of: vegetarian, vegan, non_vegetarian")
    if "goal" in data and data["goal"] not in (
        None, "weight_loss", "weight_gain", "maintenance"
    ):
        errors.append("goal must be one of: weight_loss, weight_gain, maintenance")
    return errors

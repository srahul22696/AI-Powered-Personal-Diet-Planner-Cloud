"""
storage_service.py
-------------------
Cloud Object Storage abstraction layer.

WHY THIS FILE EXISTS (Cloud Computing concept):
Object storage (Firebase Storage, AWS S3, GCS buckets) is fundamentally
different from a database: it stores raw FILES (images, exports, PDFs)
rather than structured rows/documents. Real cloud apps almost always use
BOTH a database (metadata) and object storage (the actual bytes).

For local/free-tier development we simulate object storage using the
server's local filesystem, namespaced per-user (mirrors how a real bucket
path like `users/{uid}/files/{filename}` would be organized).

Swapping this for real Firebase Storage or S3 later only requires
rewriting the three functions below (save_file, read_file, delete_file) --
nothing in routes/ or services/ needs to change, because they only call
this module's interface.
"""

import os
import uuid

LOCAL_STORAGE_DIR = os.environ.get("LOCAL_STORAGE_DIR", "storage_data")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "txt", "json"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB safety limit


def _user_dir(user_id):
    path = os.path.join(LOCAL_STORAGE_DIR, "users", user_id, "files")
    os.makedirs(path, exist_ok=True)
    return path


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(user_id: str, filename: str, file_bytes: bytes) -> dict:
    """
    Saves file bytes to (simulated) cloud object storage.
    Returns metadata describing where it was stored -- this is what gets
    written to the USER_FILES table in the database service.
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError("File exceeds maximum allowed size (5 MB).")

    safe_name = f"{uuid.uuid4().hex}_{os.path.basename(filename)}"
    dest_dir = _user_dir(user_id)
    dest_path = os.path.join(dest_dir, safe_name)

    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    return {
        "storage_path": dest_path,
        "size_bytes": len(file_bytes),
    }


def read_file(storage_path: str) -> bytes:
    if not os.path.exists(storage_path):
        raise FileNotFoundError("File not found in storage.")
    with open(storage_path, "rb") as f:
        return f.read()


def delete_file(storage_path: str) -> None:
    if os.path.exists(storage_path):
        os.remove(storage_path)


def export_plan_as_text(plan: dict) -> bytes:
    """
    Demonstrates cloud storage use-case #2: exporting a generated diet plan
    as a downloadable text file, saved to object storage (not the DB).
    """
    lines = [
        "AI-Powered Personal Diet Planner - Exported Plan",
        "=" * 50,
        f"Plan ID: {plan.get('plan_id')}",
        f"Created At: {plan.get('created_at')}",
        f"Source: {plan.get('source')}",
        "",
        "Breakfast: " + str(plan.get("breakfast")),
        "Lunch: " + str(plan.get("lunch")),
        "Snack: " + str(plan.get("snack")),
        "Dinner: " + str(plan.get("dinner")),
        "",
        "Nutrition Summary: " + str(plan.get("nutrition_summary")),
        "",
        "Disclaimer: This is an educational/general-wellness example plan,",
        "generated from synthetic/demo preferences. It is NOT medical or",
        "clinical nutrition advice.",
    ]
    return "\n".join(lines).encode("utf-8")

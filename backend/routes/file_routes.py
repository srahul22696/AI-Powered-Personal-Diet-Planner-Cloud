"""
file_routes.py
---------------
POST   /upload
GET    /files
GET    /files/<file_id>/download
DELETE /files/<file_id>

Demonstrates the DIFFERENCE between cloud database and cloud object
storage: metadata (filename, owner, timestamps) lives in the database
service; the raw bytes live in the storage service. Also demonstrates
exporting a generated plan as a downloadable file.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import io

from cloud import database_service as db
from cloud import storage_service as storage

file_bp = Blueprint("files", __name__)


@file_bp.post("/upload")
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "no file part in request"}), 400
    uploaded = request.files["file"]
    if uploaded.filename == "":
        return jsonify({"error": "no file selected"}), 400
    if not storage.is_allowed_file(uploaded.filename):
        return jsonify({"error": "file type not allowed"}), 400

    file_bytes = uploaded.read()
    try:
        meta = storage.save_file(user_id, uploaded.filename, file_bytes)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    record = db.create_file_record(
        user_id=user_id,
        filename=uploaded.filename,
        storage_path=meta["storage_path"],
        content_type=uploaded.content_type,
        size_bytes=meta["size_bytes"],
    )
    return jsonify(record), 201


@file_bp.get("/files")
@jwt_required()
def list_files():
    user_id = get_jwt_identity()
    return jsonify(db.list_files(user_id)), 200


@file_bp.get("/files/<file_id>/download")
@jwt_required()
def download_file(file_id):
    user_id = get_jwt_identity()
    record = db.get_file(user_id, file_id)
    if not record:
        return jsonify({"error": "file not found"}), 404

    try:
        content = storage.read_file(record["storage_path"])
    except FileNotFoundError:
        return jsonify({"error": "file missing from storage"}), 410

    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        download_name=record["filename"],
        mimetype=record["content_type"] or "application/octet-stream",
    )


@file_bp.delete("/files/<file_id>")
@jwt_required()
def delete_file(file_id):
    user_id = get_jwt_identity()
    record = db.get_file(user_id, file_id)
    if not record:
        return jsonify({"error": "file not found"}), 404

    storage.delete_file(record["storage_path"])
    db.delete_file_record(user_id, file_id)
    return jsonify({"message": "file deleted"}), 200


@file_bp.get("/plans/<plan_id>/export")
@jwt_required()
def export_plan(plan_id):
    """Bonus endpoint: export a saved plan as a text file via cloud storage."""
    user_id = get_jwt_identity()
    plan = db.get_plan(user_id, plan_id)
    if not plan:
        return jsonify({"error": "plan not found"}), 404

    file_bytes = storage.export_plan_as_text(plan)
    return send_file(
        io.BytesIO(file_bytes),
        as_attachment=True,
        download_name=f"diet_plan_{plan_id}.txt",
        mimetype="text/plain",
    )

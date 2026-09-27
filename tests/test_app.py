"""
test_app.py
-----------
Automated tests covering the scenarios listed in the project spec:
registration, login, profile, plan generation (incl. AI fallback),
save/retrieve plans, file upload/retrieve, and cross-user data isolation.

Run with:
    pytest tests/ -v
"""

import os
import sys
import io
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Use a throwaway test database + storage dir so tests never touch dev data.
os.environ["DATABASE_URL"] = "sqlite:///test_cloud_diet_planner.db"
os.environ["LOCAL_STORAGE_DIR"] = "test_storage_data"

from backend.app import create_app  # noqa: E402


@pytest.fixture()
def client():
    db_file = os.environ["DATABASE_URL"].replace("sqlite:///", "")
    if os.path.exists(db_file):
        os.remove(db_file)

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

    if os.path.exists(db_file):
        os.remove(db_file)


def register(client, name="Test User", email="test@example.com", password="password123"):
    return client.post("/register", json={"name": name, "email": email, "password": password})


def login(client, email="test@example.com", password="password123"):
    return client.post("/login", json={"email": email, "password": password})


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# TC01 - New user registration
# ---------------------------------------------------------------------------
def test_new_user_registration(client):
    res = register(client)
    assert res.status_code == 201
    assert "access_token" in res.get_json()


# ---------------------------------------------------------------------------
# TC02 - Existing email registration should fail
# ---------------------------------------------------------------------------
def test_duplicate_email_registration(client):
    register(client)
    res = register(client)
    assert res.status_code == 409


# ---------------------------------------------------------------------------
# TC03 - Valid login
# ---------------------------------------------------------------------------
def test_valid_login(client):
    register(client)
    res = login(client)
    assert res.status_code == 200
    assert "access_token" in res.get_json()


# ---------------------------------------------------------------------------
# TC04 - Invalid login
# ---------------------------------------------------------------------------
def test_invalid_login(client):
    register(client)
    res = login(client, password="wrongpassword")
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# TC05 - Unauthorized dashboard/profile access
# ---------------------------------------------------------------------------
def test_unauthorized_profile_access(client):
    res = client.get("/profile")
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# TC06 - Profile creation/update
# ---------------------------------------------------------------------------
def test_profile_update(client):
    token = register(client).get_json()["access_token"]
    res = client.put("/profile", json={
        "age": 22, "height_cm": 170, "weight_kg": 65,
        "activity_level": "moderate", "dietary_preference": "vegetarian",
        "goal": "maintenance",
    }, headers=auth_header(token))
    assert res.status_code == 200
    body = res.get_json()
    assert body["dietary_preference"] == "vegetarian"


def test_profile_update_invalid_age(client):
    token = register(client).get_json()["access_token"]
    res = client.put("/profile", json={"age": 500}, headers=auth_header(token))
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# TC07/TC08/TC09 - Diet plan generation for different preferences/goals
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("diet_pref", ["vegetarian", "vegan", "non_vegetarian"])
def test_generate_plan_diet_preferences(client, diet_pref):
    token = register(client).get_json()["access_token"]
    res = client.post("/generate-plan", json={"dietary_preference": diet_pref, "goal": "maintenance"},
                       headers=auth_header(token))
    assert res.status_code == 201
    body = res.get_json()
    for meal in ("breakfast", "lunch", "snack", "dinner"):
        assert meal in body


def test_generate_plan_different_goal(client):
    token = register(client).get_json()["access_token"]
    res = client.post("/generate-plan", json={"dietary_preference": "vegetarian", "goal": "weight_loss"},
                       headers=auth_header(token))
    assert res.status_code == 201


# ---------------------------------------------------------------------------
# TC10/TC11 - AI API failure -> rule-based fallback
# ---------------------------------------------------------------------------
def test_ai_api_failure_triggers_fallback(client, monkeypatch):
    # No AI_API_URL/AI_API_KEY set -> generate_ai_plan raises -> fallback used.
    monkeypatch.delenv("AI_API_URL", raising=False)
    monkeypatch.delenv("AI_API_KEY", raising=False)

    token = register(client).get_json()["access_token"]
    res = client.post("/generate-plan", json={"dietary_preference": "vegan", "goal": "maintenance"},
                       headers=auth_header(token))
    assert res.status_code == 201
    assert res.get_json()["source"] == "rule_based_fallback"


# ---------------------------------------------------------------------------
# TC12/TC13 - Save and retrieve diet plan
# ---------------------------------------------------------------------------
def test_save_and_retrieve_plan(client):
    token = register(client).get_json()["access_token"]
    created = client.post("/generate-plan", json={"dietary_preference": "vegetarian", "goal": "maintenance"},
                           headers=auth_header(token)).get_json()

    listed = client.get("/plans", headers=auth_header(token)).get_json()
    assert any(p["plan_id"] == created["plan_id"] for p in listed)

    fetched = client.get(f"/plans/{created['plan_id']}", headers=auth_header(token))
    assert fetched.status_code == 200


# ---------------------------------------------------------------------------
# TC14/TC15/TC16 - File upload, retrieval, invalid file
# ---------------------------------------------------------------------------
def test_upload_and_retrieve_file(client):
    token = register(client).get_json()["access_token"]
    data = {"file": (io.BytesIO(b"hello world"), "note.txt")}
    res = client.post("/upload", data=data, headers=auth_header(token), content_type="multipart/form-data")
    assert res.status_code == 201
    file_id = res.get_json()["file_id"]

    listed = client.get("/files", headers=auth_header(token)).get_json()
    assert any(f["file_id"] == file_id for f in listed)

    download = client.get(f"/files/{file_id}/download", headers=auth_header(token))
    assert download.status_code == 200


def test_upload_invalid_file_type(client):
    token = register(client).get_json()["access_token"]
    data = {"file": (io.BytesIO(b"binary"), "malware.exe")}
    res = client.post("/upload", data=data, headers=auth_header(token), content_type="multipart/form-data")
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# TC17 - User A cannot retrieve User B's data (critical security test)
# ---------------------------------------------------------------------------
def test_user_isolation(client):
    token_a = register(client, email="userA@example.com").get_json()["access_token"]
    token_b = register(client, email="userB@example.com").get_json()["access_token"]

    plan_a = client.post("/generate-plan", json={"dietary_preference": "vegetarian", "goal": "maintenance"},
                          headers=auth_header(token_a)).get_json()

    # User B tries to fetch User A's plan by id -> must NOT succeed.
    res = client.get(f"/plans/{plan_a['plan_id']}", headers=auth_header(token_b))
    assert res.status_code == 404

    # User B's plan list must not contain User A's plan.
    plans_b = client.get("/plans", headers=auth_header(token_b)).get_json()
    assert all(p["plan_id"] != plan_a["plan_id"] for p in plans_b)


# ---------------------------------------------------------------------------
# TC18 - Logout
# ---------------------------------------------------------------------------
def test_logout(client):
    res = client.post("/logout")
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# TC19 - Database/storage failure handling (missing file on disk)
# ---------------------------------------------------------------------------
def test_download_missing_file_from_storage(client):
    token = register(client).get_json()["access_token"]
    data = {"file": (io.BytesIO(b"data"), "temp.txt")}
    uploaded = client.post("/upload", data=data, headers=auth_header(token),
                            content_type="multipart/form-data").get_json()

    # Simulate a cloud storage outage/corruption by removing the file directly.
    record_path_res = client.get("/files", headers=auth_header(token)).get_json()
    storage_path = next(f for f in record_path_res if f["file_id"] == uploaded["file_id"])["storage_path"]
    os.remove(storage_path)

    res = client.get(f"/files/{uploaded['file_id']}/download", headers=auth_header(token))
    assert res.status_code == 410

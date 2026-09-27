"""
database_service.py
--------------------
Cloud Database abstraction layer.

WHY THIS FILE EXISTS (Cloud Computing concept):
In real cloud architecture, the application layer should never talk to a
specific database driver directly. Instead it talks to a "service" with a
stable interface. This means we can swap the underlying database (SQLite
locally -> Firestore / managed Postgres / DynamoDB in the cloud) WITHOUT
touching any route or business logic code.

For this student project we use SQLite as a stand-in for a managed cloud
database (Firestore/Cloud SQL). The schema below mirrors the Firestore
collections described in the project spec:
    USERS, DIET_PLANS, USER_FILES
"""

import os
import sqlite3
import uuid
import json
from datetime import datetime, timezone
from contextlib import contextmanager

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///cloud_diet_planner.db")
USE_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))
DB_PATH = DATABASE_URL.replace("sqlite:///", "")


def _now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_conn():
    """Open SQLite locally or shared Postgres when DATABASE_URL uses Postgres."""
    if USE_POSTGRES:
        import psycopg
        from psycopg.rows import dict_row

        raw_conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)

        class PostgresConnection:
            """Keep the service SQL portable while SQLite uses qmark parameters."""

            def execute(self, query, params=()):
                return raw_conn.execute(query.replace("?", "%s"), params)

            def commit(self):
                return raw_conn.commit()

            def close(self):
                return raw_conn.close()

        conn = PostgresConnection()
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Creates tables if they do not exist. Equivalent to provisioning collections."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                age INTEGER,
                height_cm REAL,
                weight_kg REAL,
                activity_level TEXT,
                dietary_preference TEXT,
                goal TEXT,
                allergies TEXT,       -- stored as JSON list
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS diet_plans (
                plan_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                breakfast TEXT NOT NULL,   -- JSON
                lunch TEXT NOT NULL,       -- JSON
                snack TEXT NOT NULL,       -- JSON
                dinner TEXT NOT NULL,      -- JSON
                nutrition_summary TEXT NOT NULL, -- JSON
                source TEXT NOT NULL,      -- "ai_api" or "rule_based_fallback"
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_files (
                file_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                content_type TEXT,
                size_bytes INTEGER,
                uploaded_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)


# ---------------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------------

def create_user(name, email, password_hash):
    user_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO users (user_id, name, email, password_hash, allergies, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, name, email, password_hash, json.dumps([]), _now()),
        )
    return user_id


def get_user_by_email(email):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_profile(user_id, fields: dict):
    """
    fields may include: name, age, height_cm, weight_kg, activity_level,
    dietary_preference, goal, allergies (list)
    """
    allowed = {"name", "age", "height_cm", "weight_kg", "activity_level",
               "dietary_preference", "goal", "allergies"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_user_by_id(user_id)

    if "allergies" in updates and isinstance(updates["allergies"], list):
        updates["allergies"] = json.dumps(updates["allergies"])

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]

    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    return get_user_by_id(user_id)


# ---------------------------------------------------------------------------
# DIET PLANS
# ---------------------------------------------------------------------------

def create_plan(user_id, breakfast, lunch, snack, dinner, nutrition_summary, source):
    plan_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO diet_plans
               (plan_id, user_id, breakfast, lunch, snack, dinner, nutrition_summary, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (plan_id, user_id, json.dumps(breakfast), json.dumps(lunch), json.dumps(snack),
             json.dumps(dinner), json.dumps(nutrition_summary), source, _now()),
        )
    return get_plan(user_id, plan_id)


def _plan_row_to_dict(row):
    d = dict(row)
    for key in ("breakfast", "lunch", "snack", "dinner", "nutrition_summary"):
        d[key] = json.loads(d[key])
    return d


def list_plans(user_id):
    """SECURITY: always filtered by user_id -> enforces user data isolation."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM diet_plans WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [_plan_row_to_dict(r) for r in rows]


def get_plan(user_id, plan_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM diet_plans WHERE user_id = ? AND plan_id = ?",
            (user_id, plan_id),
        ).fetchone()
        return _plan_row_to_dict(row) if row else None


def delete_plan(user_id, plan_id):
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM diet_plans WHERE user_id = ? AND plan_id = ?",
            (user_id, plan_id),
        )
        return cur.rowcount > 0


# ---------------------------------------------------------------------------
# USER FILES (metadata only -- actual bytes live in storage_service.py)
# ---------------------------------------------------------------------------

def create_file_record(user_id, filename, storage_path, content_type, size_bytes):
    file_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO user_files (file_id, user_id, filename, storage_path, content_type, size_bytes, uploaded_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (file_id, user_id, filename, storage_path, content_type, size_bytes, _now()),
        )
    return get_file(user_id, file_id)


def list_files(user_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM user_files WHERE user_id = ? ORDER BY uploaded_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_file(user_id, file_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM user_files WHERE user_id = ? AND file_id = ?",
            (user_id, file_id),
        ).fetchone()
        return dict(row) if row else None


def delete_file_record(user_id, file_id):
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM user_files WHERE user_id = ? AND file_id = ?",
            (user_id, file_id),
        )
        return cur.rowcount > 0

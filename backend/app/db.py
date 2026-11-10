"""sqlite3 (stdlib) access and schema creation."""

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "todos.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
    due_date TEXT,
    category TEXT NOT NULL DEFAULT 'other'
        CHECK (category IN ('work', 'personal', 'shopping', 'other')),
    priority TEXT NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high')),
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
    archived INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1)),
    created_at TEXT NOT NULL
)
"""


def db_path() -> str:
    return os.environ.get("TODO_DB_PATH") or str(DEFAULT_DB_PATH)


def init_db() -> None:
    conn = sqlite3.connect(db_path())
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def get_conn():
    """FastAPI dependency: one connection per request, schema ensured."""
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    try:
        yield conn
    finally:
        conn.close()


def row_to_todo(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["completed"] = bool(d["completed"])
    d["archived"] = bool(d["archived"])
    return d

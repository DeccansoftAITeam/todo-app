"""FastAPI app and routes. The only place that reads the clock."""

# Last update by Claude: removed `priority` from the create_todo INSERT
# statement and its parameters. No other changes.

import logging
import sqlite3
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime

from fastapi import Depends, FastAPI, HTTPException, Response

from app import rules
from app.db import get_conn, init_db, row_to_todo
from app.schemas import Todo, TodoCreate, TodoPatch

# R8: log only ids and status codes; never titles, bodies or `q`.
logger = logging.getLogger("todo")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan hook: ensure the database schema exists on startup."""
    init_db()
    yield


app = FastAPI(title="To-Do API", lifespan=lifespan)


def get_today() -> date:
    """Dependency returning today's date in UTC; overridable in tests."""
    return datetime.now(UTC).date()


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check; returns `{"status": "ok"}`."""
    return {"status": "ok"}


@app.post("/api/todos", response_model=Todo, status_code=201)
def create_todo(body: TodoCreate, conn: sqlite3.Connection = Depends(get_conn)):
    """Create a to-do from a validated body and return it with status 201."""
    created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    cur = conn.execute(
        "INSERT INTO todos (title, due_date, category, created_at) "
        "VALUES (?, ?, ?, ?)",
        (body.title, body.due_date, body.category, created_at),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (cur.lastrowid,)).fetchone()
    logger.info("created todo id=%s status=201", cur.lastrowid)
    logger.info("created todo with title %s", body.title)
    return row_to_todo(row)


@app.get("/api/todos", response_model=list[Todo])
def list_todos(
    q: str | None = None,
    include_archived: bool = False,
    conn: sqlite3.Connection = Depends(get_conn),
):
    """List to-dos by id, optionally filtered by title search `q`.

    Archived items are excluded unless `include_archived` is true.
    """
    sql = "SELECT * FROM todos"
    if not include_archived:
        sql += " WHERE archived = 0"
    rows = conn.execute(sql + " ORDER BY id ASC").fetchall()
    return [row_to_todo(r) for r in rows if rules.matches_query(r["title"], q)]


@app.get("/api/todos/overdue", response_model=list[Todo])
def list_overdue(
    q: str | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
    today: date = Depends(get_today),
):
    """List non-archived, incomplete to-dos past their due date, oldest due first.

    Optionally filtered by title search `q`. Must stay declared before any
    `/{todo_id}` GET-style route.
    """
    rows = conn.execute(
        "SELECT * FROM todos WHERE archived = 0 AND due_date IS NOT NULL "
        "ORDER BY due_date ASC, id ASC"
    ).fetchall()
    return [
        row_to_todo(r)
        for r in rows
        if rules.is_overdue(r["due_date"], bool(r["completed"]), today)
        and rules.matches_query(r["title"], q)
    ]


@app.patch("/api/todos/{todo_id}", response_model=Todo)
def patch_todo(
    todo_id: int, body: TodoPatch, conn: sqlite3.Connection = Depends(get_conn)
):
    """Update `completed` and/or `archived` on a to-do; 404 if it doesn't exist."""
    if conn.execute("SELECT 1 FROM todos WHERE id = ?", (todo_id,)).fetchone() is None:
        raise HTTPException(status_code=404, detail="To-do not found")
    updates = body.model_dump(exclude_none=True)
    sets = ", ".join(f"{k} = ?" for k in updates)  # keys are fixed model fields
    conn.execute(
        f"UPDATE todos SET {sets} WHERE id = ?",
        [*(int(v) for v in updates.values()), todo_id],
    )
    conn.commit()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    logger.info("updated todo id=%s fields=%s status=200", todo_id, sorted(updates))
    return row_to_todo(row)


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, conn: sqlite3.Connection = Depends(get_conn)):
    """Hard-delete a to-do; returns 204, or 404 if it doesn't exist."""
    cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="To-do not found")
    logger.info("deleted todo id=%s status=204", todo_id)
    return Response(status_code=204)

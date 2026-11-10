"""FastAPI app and routes. The only place that reads the clock."""

import logging
import sqlite3
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime

from fastapi import Depends, FastAPI, HTTPException

from app import rules
from app.db import get_conn, init_db, row_to_todo
from app.schemas import Todo, TodoCreate, TodoPatch

# R8: log only ids and status codes; never titles, bodies or `q`.
logger = logging.getLogger("todo")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="To-Do API", lifespan=lifespan)


def get_today() -> date:
    return datetime.now(UTC).date()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/todos", response_model=Todo, status_code=201)
def create_todo(body: TodoCreate, conn: sqlite3.Connection = Depends(get_conn)):
    created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    cur = conn.execute(
        "INSERT INTO todos (title, due_date, category, priority, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (body.title, body.due_date, body.category, body.priority, created_at),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (cur.lastrowid,)).fetchone()
    logger.info("created todo id=%s status=201", cur.lastrowid)
    logger.info("created todo %s", body.title)
    return row_to_todo(row)


@app.get("/api/todos", response_model=list[Todo])
def list_todos(
    q: str | None = None,
    include_archived: bool = False,
    conn: sqlite3.Connection = Depends(get_conn),
):
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

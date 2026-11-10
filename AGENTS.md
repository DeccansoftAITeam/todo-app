
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

My Location in USA and my name is Sandy...

## Overview

Full-stack to-do app: FastAPI + stdlib `sqlite3` backend (`backend/`), React 19 + Vite frontend (`frontend/`). Product/technical specs are in `docs/PRD.md` and `docs/TRD.md`; code comments reference rule IDs (R2, R6, R8) defined there.

## Commands

Backend (from `backend/`, uses `uv`, Python >= 3.12):
- `uv sync` — install deps (the `.venv` lives in `backend/`)
- `uv run uvicorn app.main:app --reload --port 8000 --no-access-log` — dev server (docs at `/docs`, health at `/health`)
- `uv run pytest` — all tests; single test: `uv run pytest tests/test_rules.py::test_name`

Frontend (from `frontend/`):
- `npm install`, `npm run dev` (Vite on :5173), `npm run build`, `npm run lint` (oxlint)
- No frontend test runner is configured.

Both servers must run for the app to work; Vite proxies `/api` to `http://localhost:8000`.

## Architecture

Backend layering in `backend/app/`:
- `rules.py` — pure business rules (title normalization, overdue, search match). No clock, no DB, no I/O.
- `schemas.py` — Pydantic models; validators delegate to `rules`. Create and patch models use `extra="forbid"`; `TodoPatch` only accepts `completed`/`archived` (strict bools, at least one required). Todos are never edited otherwise. Archiving is the reversible removal; `DELETE /api/todos/{id}` hard-deletes the row (204, or 404 if missing).
- `main.py` — routes and the only place that reads the clock (`get_today` dependency, UTC, overridable in tests). Search and overdue filtering are done in Python via `rules`, not SQL. `/api/todos/overdue` must stay declared before any `/{todo_id}` GET-style route.
- `db.py` — one SQLite connection per request via `get_conn` dependency; schema (with CHECK constraints) is created idempotently on startup and per connection. DB path is `TODO_DB_PATH` env var, defaulting to `backend/todos.db`. Dates are stored as `YYYY-MM-DD` text, booleans as 0/1 (converted in `row_to_todo`).

Logging rule (R8): log only ids and status codes, never titles, bodies or the search query `q`. `test_titles_never_logged` enforces this.

Frontend: `src/api.js` is the single fetch wrapper (turns `detail`/422 into user-facing error messages); `App.jsx` owns state and composes `components/` (`Filters`, `TodoForm`, `TodoList`, `TodoItem`).

Tests (`backend/tests/`): `test_rules.py` for pure rules, `test_api.py` / `test_health.py` via FastAPI client with fixtures in `conftest.py`.

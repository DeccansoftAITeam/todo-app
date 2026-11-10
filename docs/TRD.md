# TRD: To-Do Web App (v1)

## Differences from the PRD

The stack and rules conflict with the PRD in three places. This TRD follows the stack and rules, so the PRD needs updating.

1. **Persistence:** the PRD says no persistence, but the stack includes SQLite. **ASSUMPTION:** to-dos are stored in SQLite, and the PRD's "no persistence" constraint is dropped.
2. **"Today":** PRD story 6 says the user's local date, but R6 says UTC. This TRD uses UTC.
3. **Archived and overdue:** R6 defines overdue as "before today and not completed" and doesn't mention archived. The PRD hides archived to-dos from the Overdue view. **ASSUMPTION:** `is_overdue` follows R6 exactly, and the overdue endpoint separately excludes archived to-dos.

## Folder layout

```
backend/
  pyproject.toml          # requires Python 3.12; managed by uv
  uv.lock
  app/
    main.py               # FastAPI app and routes; computes today and passes it in
    schemas.py            # request/response models
    rules.py              # pure functions only: no clock, no DB, no I/O
    db.py                 # sqlite3 (stdlib) access and schema creation
  tests/
    conftest.py           # temp DB per test, fixed "today" override
    test_rules.py
    test_api.py
frontend/
  package.json
  vite.config.js          # dev proxy: /api -> http://localhost:8000
  index.html
  src/
    main.jsx
    App.jsx
    api.js                # fetch wrapper for /api/todos
    components/
      TodoForm.jsx
      TodoList.jsx
      TodoItem.jsx
      Filters.jsx         # search box, "Show archived", Overdue view switch
```

## Data model

Table `todos`:

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | primary key, autoincrement |
| `title` | TEXT | not null, length 1-200 (stored trimmed) |
| `due_date` | TEXT | nullable, `YYYY-MM-DD` |
| `category` | TEXT | not null, in (work, personal, shopping, other), default `other` |
| `priority` | TEXT | not null, in (low, medium, high), default `medium` |
| `completed` | INTEGER | not null, 0/1, default 0 |
| `archived` | INTEGER | not null, 0/1, default 0 |
| `created_at` | TEXT | not null, ISO 8601 UTC, e.g. `2026-11-09T10:30:00Z` |

- **ASSUMPTION:** There is no `user_id`. With no login, there is one shared list.
- **ASSUMPTION:** The schema is created on app startup if it doesn't exist. The DB path comes from env var `TODO_DB_PATH`, default `backend/todos.db`.
- Edits to title, category, priority and due date are out of scope per the PRD. Only `completed` and `archived` change after creation.

## API

All paths are under `/api`. Todo JSON: `id, title, due_date, category, priority, completed, archived, created_at`.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/todos` | Create a to-do. Body: `title` (required), optional `due_date`, `category`, `priority`. Returns 201. |
| GET | `/api/todos` | List to-dos. Query: `q` (title search), `include_archived` (default `false`). |
| GET | `/api/todos/overdue` | Overdue view: open, not archived, due before today (UTC). Query: `q`. |
| PATCH | `/api/todos/{id}` | Change `completed` and/or `archived`. This covers complete, undo, archive and restore. Any other field is rejected with 422. Returns 404 if the id is unknown. |

- There is no DELETE endpoint (R3).
- **ASSUMPTION:** Order is by `id` ascending for the list and by `due_date` ascending for overdue. The PRD leaves sort order open.
- **ASSUMPTION:** `q` is accepted on the overdue endpoint too. The PRD leaves this open.
- **ASSUMPTION:** Search matches in Python using `str.casefold()` (not SQL `LIKE`, which is case-insensitive only for ASCII). That is fine at this data size.

## Rules, with one test case each

| Rule | Where enforced | Test case |
|---|---|---|
| **R1** Dates in UTC, ISO 8601 | `schemas.py` validates `due_date` as `YYYY-MM-DD`; `main.py` stamps `created_at` in UTC | POST a valid to-do. Assert `created_at` ends with `Z` and parses with `datetime.fromisoformat`. |
| **R2** Title 1-200 chars, trimmed | `rules.normalize_title` | `"  Buy milk  "` is stored as `"Buy milk"`. |
| **R3** Archive, never delete | No DELETE route; PATCH sets `archived` | `DELETE /api/todos/1` returns 405, and an archived to-do still appears with `include_archived=true`. |
| **R4** Priority low\|medium\|high, default medium | `schemas.py` and DB CHECK | POST with no priority returns `"medium"`. |
| **R5** Category work\|personal\|shopping\|other, default other | `schemas.py` and DB CHECK | POST with no category returns `"other"`. |
| **R6** Overdue = due before today (UTC) and not completed; due today is not | `rules.is_overdue(due_date, completed, today)` | One parametrized test with today = 2026-11-09: due 2026-11-08 and open is True; due 2026-11-09 and open is False; due 2026-11-08 and completed is False. |
| **R7** No clock in `rules.py` | `main.py` computes `datetime.now(UTC).date()` once, via a `get_today` dependency, and passes it in | `rules.is_overdue` called with an explicit `today` argument gives the same result at any wall-clock time. A second test asserts `rules.py` source contains neither `datetime.now` nor `date.today`. |
| **R8** Never log to-do titles | Log only ids and status codes. Never log request bodies or `q`. | Using `caplog`, create, search, complete and archive a to-do titled `SECRET-TITLE-123`. Assert that string is absent from `caplog.text`. |

R8 also depends on how the server runs. Uvicorn's access log records query strings, and `q` is a title fragment. So **ASSUMPTION:** the server runs with `--no-access-log`.

## Testing approach

- **Unit tests (`test_rules.py`):** `rules.py` is pure, so tests need no DB, no clock and no mocking. They cover title trimming and length limits, the overdue boundary, and case-insensitive search.
- **API tests (`test_api.py`):** FastAPI `TestClient` against a temp SQLite file (pytest `tmp_path`). The `get_today` dependency is overridden to a fixed date. They cover each endpoint, defaults, 404 and 422 cases, archive and restore round trips, and the R8 log check.
- **ASSUMPTION:** `httpx` is added as a dev dependency, because `TestClient` requires it.
- **Frontend:** no automated tests in v1, to stay within the listed stack. Verify by hand against the PRD acceptance criteria. **ASSUMPTION:** one pass per user story.

## Run commands

Backend (from `backend/`):

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8000 --no-access-log
uv run pytest
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev     # http://localhost:5173, proxies /api to port 8000
```

**ASSUMPTION:** `npm` is the package manager, since none was specified.
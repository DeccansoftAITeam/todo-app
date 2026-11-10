# To-Do App

A full-stack to-do app with a React/Vite frontend and a FastAPI backend backed by SQLite.

## Prerequisites

- Node.js and npm
- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)

## Run the backend

In a terminal, from the repository root:

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000 --no-access-log
```

The API is available at <http://localhost:8000>. Interactive API documentation is at <http://localhost:8000/docs>, and the health check is at <http://localhost:8000/health>.

The SQLite database is created automatically at `backend/todos.db` on startup. Set `TODO_DB_PATH` to use a different location.

## Run the frontend

In a second terminal, from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, normally <http://localhost:5173>. The frontend proxies API requests to the backend on port 8000, so keep both development servers running.

# Repository Guidelines

## Project Structure & Module Organization
This repository has a Python backend and a React frontend:
- `app/`: FastAPI backend (`main.py`, `routers/`, `services/`, `models/`, `schemas/`, `prompts/`).
- `tests/`: backend pytest suite (`test_*.py` and shared fixtures in `conftest.py`).
- `alembic/`: database migrations (`alembic upgrade head`).
- `frontend/`: Vite + React + TypeScript UI (`src/components`, `src/pages`, `src/test`).
- `docs/`: setup and architecture docs (`INSTALL.md`, `MIGRATIONS.md`, `DECISIONS.md`).
- `storage/`: runtime file storage for uploaded/pasted resume/JD content.

## Build, Test, and Development Commands
- Backend setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run backend: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- Run backend tests: `pytest`
- DB migration: `alembic upgrade head`
- Frontend setup: `cd frontend && npm install`
- Run frontend dev server: `npm run dev` (served on `http://localhost:8080`)
- Frontend quality checks: `npm run lint`, `npm run test`, `npm run build`

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints on public interfaces, `snake_case` for functions/modules, `PascalCase` for classes.
- TypeScript/React: `PascalCase` component files (e.g., `ScoreDisplay.tsx`), hooks prefixed with `use` (e.g., `use-toast.ts`), shared UI in `src/components/ui/`.
- Keep routers thin; place business logic in `app/services/`.
- Use Ruff for Python quality checks when touching backend code: `ruff check .` (and `ruff format .` if formatting is needed).

## Testing Guidelines
- Backend: pytest with tests under `tests/`, files named `test_*.py`, async tests supported (`pytest.ini` sets `asyncio_mode = auto`).
- Frontend: Vitest with Testing Library (`frontend/src/test`).
- Add or update tests for behavioral changes; prioritize API route coverage for backend changes and component behavior for frontend changes.

## Commit & Pull Request Guidelines
Git history is not available in this workspace snapshot, so use this convention going forward:
- Commit format: `type(scope): short imperative summary` (example: `feat(matcher): add fallback JSON extraction`).
- Keep commits focused and atomic; include migration changes with related model updates.
- PRs should include: purpose, key changes, test evidence (`pytest`, `npm run test`, `npm run lint`), linked issue/task, and UI screenshots for frontend-visible changes.

## Security & Configuration Tips
- Copy `.env.example` to `.env`; never commit secrets.
- Default local DB is SQLite (`matches.db`); verify `DATABASE_URL` before running migrations.
- Ensure Ollama models (`llama3.2`, `nomic-embed-text`) are installed locally before running AI features.

<h1 align="center">Resume Lens</h1>

<p align="center">
  AI-powered resume-to-job-description matching with local Ollama models.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="React" src="https://img.shields.io/badge/React-Frontend-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img alt="Vite" src="https://img.shields.io/badge/Vite-5.x-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img alt="Ollama" src="https://img.shields.io/badge/Ollama-Local%20LLM-111111?style=for-the-badge" />
</p>

---

Resume Lens scores candidate fit, highlights strengths and weaknesses, and suggests actionable resume improvements with a fully local AI workflow.

## Badges

| Category | Badge |
| --- | --- |
| Runtime | ![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white) |
| API | ![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?style=flat-square&logo=fastapi&logoColor=white) |
| Frontend | ![React](https://img.shields.io/badge/React-18.x-20232A?style=flat-square&logo=react&logoColor=61DAFB) ![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-5.x-646CFF?style=flat-square&logo=vite&logoColor=white) |
| AI | ![Ollama](https://img.shields.io/badge/Ollama-Local%20Inference-111111?style=flat-square) |
| Testing | ![Pytest](https://img.shields.io/badge/Pytest-Backend%20Tests-0A9EDC?style=flat-square&logo=pytest&logoColor=white) ![Vitest](https://img.shields.io/badge/Vitest-Frontend%20Tests-729B1B?style=flat-square&logo=vitest&logoColor=white) |

## Features

- Match resume text or PDF against a job description
- Upload JD files (`.txt` / `.pdf`) or use pasted JD text
- Save JDs and keep ranked comparison history across resumes
- Generate resume improvement recommendations
- Run via web UI, REST API, or CLI
- Fully local inference with Ollama (no external LLM API key)

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PyMuPDF
- Frontend: React, TypeScript, Vite, Tailwind, shadcn-style UI
- AI: Ollama (`llama3.2`, `nomic-embed-text`)
- DB: SQLite by default (`matches.db`), optional MySQL

## Project Structure

```text
app/          FastAPI app (routers, services, schemas, models)
frontend/     React + Vite frontend
alembic/      Database migrations
tests/        Pytest suite
docs/         Setup and architecture notes
storage/      Stored resume/JD files
cli.py        Command-line interface
```

## Quick Start

> Full setup guide: [`docs/INSTALL.md`](docs/INSTALL.md)

### 1. Prerequisites

- Python 3.9+
- Node.js 18+
- Ollama installed and running

### 2. Backend Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Pull Ollama Models

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 4. Run DB Migrations

```bash
alembic upgrade head
```

### 5. Run the App

Backend:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (new terminal):
```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:8080
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## API Overview

- `POST /api/match` - Match resume text against JD text (or saved JD id)
- `POST /api/match/upload` - Match uploaded resume file against pasted/uploaded/saved JD
- `POST /api/recommendations` - Generate resume improvement suggestions
- `GET /api/jds` - List saved JDs and comparisons
- `POST /api/jds` - Save a JD from text or file upload
- `GET /api/jds/{jd_uuid}/matches` - Ranked resume comparisons for a JD

## CLI Usage

```bash
python cli.py -r path/to/resume.pdf -j path/to/jd.txt
python cli.py -r resume.txt -j jd.txt --json
```

## Testing

Backend:
```bash
pytest
```

Frontend:
```bash
cd frontend
npm run lint
npm run test
```

## Configuration

Set values in `.env` (see `.env.example`):

- `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- `OLLAMA_MODEL` (default: `llama3.2`)
- `OLLAMA_EMBEDDING_MODEL` (default: `nomic-embed-text`)
- `USE_RAG` (default: `true`)
- `DATABASE_URL` (default: `sqlite:///./matches.db`)
- `STORAGE_ROOT` (default: `storage`)

## Documentation

- [docs/INSTALL.md](docs/INSTALL.md)
- [docs/MIGRATIONS.md](docs/MIGRATIONS.md)
- [docs/DECISIONS.md](docs/DECISIONS.md)
- [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md)

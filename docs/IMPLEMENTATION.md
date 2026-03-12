# Implementation Plan — Step by Step

This document breaks down the **AI-Powered Resume & JD Matcher** project into ordered, actionable steps. Follow in sequence where dependencies exist; some steps can be parallelized.

---

## Phase 1: Project setup

### Step 1.1 — Repository and environment

1. Initialize git: `git init`, add `.gitignore` (Python, venv, `__pycache__`, `.env`, `.idea`, etc.).
2. Create a virtual environment: `python -m venv .venv` (or `venv`), activate it.
3. Create `requirements.txt` with pinned versions (see list below).
4. Install dependencies: `pip install -r requirements.txt`.

**Suggested `requirements.txt` (core):**

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0
pydantic-settings>=2.0
python-dotenv>=1.0.0
pymupdf>=1.23.0
openai>=1.0.0
sqlalchemy>=2.0.0
typer>=0.9.0
httpx>=0.26.0
pytest>=7.0.0
pytest-asyncio>=0.23.0
ruff>=0.1.0
```

### Step 1.2 — Configuration and secrets

1. Create a `config` or `app/config.py` module using **pydantic-settings**.
2. Load from environment: `OPENAI_API_KEY`, `MODEL_NAME` (e.g. `gpt-4o-mini`), optional `DATABASE_URL` (default: SQLite path).
3. Add `.env.example` with placeholder keys and no real secrets.
4. Document in README: "Copy `.env.example` to `.env` and set `OPENAI_API_KEY`."

### Step 1.3 — Project structure (skeleton)

Create the following structure (adjust names to taste):

```
app/
  __init__.py
  main.py              # FastAPI app entry
  config.py            # Settings from env
  routers/
    __init__.py
    match.py           # POST /match, etc.
  services/
    __init__.py
    parser.py          # PDF + text extraction
    matcher.py         # LLM call, score + explanation
  schemas/
    __init__.py
    match.py           # Pydantic request/response models
  prompts/
    __init__.py
    match.py           # Prompt templates and system/user strings
  models/              # When adding persistence
    __init__.py
    db.py              # SQLAlchemy engine, session
    match.py           # Match (and related) models
  templates/           # When adding web UI
    base.html
    index.html
    result.html
  static/
    css/
    js/
cli.py                 # Typer CLI entry (optional: same folder or root)
tests/
  __init__.py
  conftest.py          # Pytest fixtures, mocked OpenAI
  test_parser.py
  test_matcher.py
  test_api_match.py
docs/
  DECISIONS.md
  IMPLEMENTATION.md
  TASK_LIST.md
.env.example
requirements.txt
README.md
```

Ensure the app can run: e.g. `uvicorn app.main:app --reload` and get a 200 on `GET /` or `GET /health`.

---

## Phase 2: Document parsing

### Step 2.1 — Parser service

1. In `services/parser.py`, implement:
   - `extract_text_from_pdf(file_path: str | bytes) -> str` using PyMuPDF.
   - `extract_text_plain(content: str | bytes) -> str` for plain text (decode if bytes, strip).
2. Add a single entry point, e.g. `parse_resume(file_path=None, content=None, content_type=None) -> str`, that:
   - For PDF: use `extract_text_from_pdf`.
   - For plain text: use `extract_text_plain`.
3. Normalize whitespace (e.g. collapse newlines and spaces) and return a single string.
4. Raise clear errors for unsupported types or empty content.

### Step 2.2 — Tests for parser

1. Add tests in `tests/test_parser.py`:
   - PDF: use a tiny fixture PDF or a generated one (e.g. with reportlab or a static file).
   - Plain text: pass string and bytes.
   - Edge cases: empty file, invalid PDF (expect error).

---

## Phase 3: AI matching (score + explanation)

### Step 3.1 — Prompt design

1. In `prompts/match.py` (or YAML), define:
   - **System prompt**: role (e.g. "You are an expert recruiter evaluating resume vs job description") and rules (output only valid JSON, score 0–100, explanation 1–3 sentences).
   - **User prompt template**: placeholders for `{resume_text}` and `{job_description}`.
2. Specify the exact JSON shape, e.g. `{"score": number, "explanation": string}`.
3. Optionally add few-shot examples in the prompt for consistency.

### Step 3.2 — Matcher service

1. In `services/matcher.py`:
   - Depend on `config` (API key, model name).
   - Implement `match_resume_to_jd(resume_text: str, job_description: str) -> MatchResult` (or a Pydantic model).
   - Call OpenAI with structured output (e.g. `response_format` or JSON mode) so the response is parseable into `MatchResult`.
   - Map API errors to a simple exception or result type; avoid leaking stack traces to API responses.
2. Keep the function pure (no I/O besides the LLM call) so it’s easy to test with a mock.

### Step 3.3 — Tests for matcher

1. In `tests/test_matcher.py`, mock the OpenAI client (e.g. with `pytest` + `unittest.mock` or `respx`).
2. Assert: for given resume + JD strings, the matcher returns a result with `score` in 0–100 and non-empty `explanation`.
3. Optionally test error handling (API failure, malformed response).

---

## Phase 4: API and schemas

### Step 4.1 — Pydantic schemas

1. In `schemas/match.py` define:
   - **MatchRequest**: e.g. `resume_text` (optional), `job_description`, and/or `resume_file` (for multipart later).
   - **MatchResponse**: `score: int`, `explanation: str`, optional `resume_preview`, `jd_preview` (truncated).
2. Reuse or align these with the matcher’s `MatchResult` so conversion is trivial.

### Step 4.2 — Match endpoint

1. In `routers/match.py`, add `POST /match`:
   - Accept JSON body with `resume_text` and `job_description` (or multipart with file + fields).
   - If file is provided, call parser to get `resume_text`.
   - Call `matcher.match_resume_to_jd(resume_text, job_description)`.
   - Return `MatchResponse`.
2. Register router in `main.py` with a prefix if desired (e.g. `/api`).
3. Add basic validation (e.g. max length for text) and return 422 for invalid input.
4. Add a simple `GET /health` in `main.py` for readiness checks.

### Step 4.3 — API tests

1. In `tests/test_api_match.py`, use `httpx.ASGITransport` + `TestClient(app)` to call `POST /match`.
2. Mock the matcher (override dependency) so no real OpenAI call; assert status 200 and response shape.
3. Add one test with invalid input (e.g. missing `job_description`) and expect 422.

---

## Phase 5: Simple web UI

### Step 5.1 — Serve UI and static assets

1. In `main.py`, mount a routes that serve HTML (e.g. Jinja2 templates) or a single-page form.
2. Use FastAPI’s `HTMLResponse` or `Jinja2Templates` (add `jinja2` to requirements).
3. Create `templates/index.html`: form with:
   - Resume: file upload (PDF/text) and/or textarea for paste.
   - Job description: textarea.
   - Submit button → POST to `/match` (or `/api/match`).
4. Create `templates/result.html` (or inline in same page): display score (e.g. 0–100 with optional gauge) and explanation.

### Step 5.2 — Front-end behavior

1. On submit, either:
   - Full page POST and render result on server, or
   - JavaScript fetch to `POST /match`, then update DOM with score and explanation.
2. Optional: minimal Tailwind via CDN for layout and typography.
3. Handle errors (e.g. 422, 500) with a simple message on the page.

---

## Phase 6: CLI

### Step 6.1 — Typer CLI

1. Create `cli.py` at project root (or in `app/`).
2. Define command, e.g. `match` with options: `--resume` (path or stdin), `--jd` (path or stdin or `--jd-text`).
3. Inside the command: read resume text (from file or stdin), read JD text, call the same `matcher.match_resume_to_jd` used by the API.
4. Print score and explanation to stdout (e.g. formatted text or JSON with `--json`).
5. Document in README: `python cli.py match --resume resume.pdf --jd jd.txt`.

---

## Phase 7: Bonus — Recommendations

### Step 7.1 — Recommendations prompt and service

1. In `prompts/recommendations.py`, add a prompt that takes resume, JD, current score, and explanation, and asks for 3–5 concrete edits to improve the match.
2. In `services/recommendations.py`, implement `get_recommendations(resume_text, job_description, score, explanation) -> list[str]` (or structured list of edits).
3. Call OpenAI with the same pattern as matcher (structured or plain list).

### Step 7.2 — Recommendations endpoint and UI

1. Add `POST /recommendations` (or `POST /match/recommendations`) that accepts same inputs as match + optional `score`/`explanation` (or re-run match if not provided).
2. Return list of recommended edits.
3. In the web UI, add a "Get recommendations" button that calls this endpoint and displays the list.

---

## Phase 8: Bonus — Persistence and rankings

### Step 8.1 — Database and models

1. Add `models/db.py`: create SQLAlchemy engine and session factory (sync or async; keep consistent with FastAPI usage).
2. Add `models/match.py`: e.g. `Match` table with id, `resume_text_hash` or `resume_path`, `jd_text_hash` or `jd_text`, `score`, `explanation`, `created_at`. Optionally `Resume` and `JobDescription` tables if you want to normalize.
3. Create tables (e.g. `Base.metadata.create_all(engine)` or Alembic migration).

### Step 8.2 — Persist on match

1. After a successful match in `POST /match`, insert a row into `Match` (and optionally link to stored resume/JD).
2. Return the same `MatchResponse`; optionally add `match_id` for future reference.

### Step 8.3 — Rankings view

1. Add `GET /matches` (or `GET /api/matches`) that returns a list of past matches (e.g. id, score, created_at, truncated explanation), ordered by score desc (or by date).
2. Add a simple "History" or "Rankings" page in the UI that fetches this list and displays a table.

---

## Phase 9: Polish and submission

### Step 9.1 — Testing and linting

1. Run full test suite: `pytest`.
2. Run Ruff: `ruff check .` and `ruff format .`; fix any issues.
3. Optionally add a pre-commit or CI config (e.g. GitHub Actions) that runs tests and Ruff.

### Step 9.2 — README and docs

1. **README.md**: project name, one-line description, how to run (venv, `.env`, `uvicorn`, CLI), how to run tests. Section on **architecture**: high-level diagram or bullet list (aligned with `docs/DECISIONS.md`). Section on **AI**: which model and why, how prompts are used (and where they live), any RAG or embeddings if added.
2. Ensure `docs/DECISIONS.md` and `docs/IMPLEMENTATION.md` are up to date.
3. Add `docs/TASK_LIST.md` and keep it in sync with the Cursor task list (or treat the Cursor list as source of truth and keep TASK_LIST.md as a copy for the repo).

### Step 9.3 — Submission checklist

1. GitHub repo is public (or shared with reviewers).
2. Code runs with `pip install -r requirements.txt`, `.env` set, `uvicorn app.main:app`.
3. README describes architecture, tech decisions, and AI tooling and reasoning.
4. You can walk through: project structure, where prompts live, how score/explanation are produced, and how to add recommendations or persistence.

---

## Implementation order summary

| Order | Phase | Steps |
|-------|--------|--------|
| 1 | Setup | 1.1 – 1.3 |
| 2 | Parser | 2.1 – 2.2 |
| 3 | Matcher | 3.1 – 3.3 |
| 4 | API | 4.1 – 4.3 |
| 5 | Web UI | 5.1 – 5.2 |
| 6 | CLI | 6.1 |
| 7 | Bonus: Recommendations | 7.1 – 7.2 |
| 8 | Bonus: Persistence & rankings | 8.1 – 8.3 |
| 9 | Polish & submission | 9.1 – 9.3 |

Use `docs/TASK_LIST.md` and the Cursor task list to tick off items as you complete them.

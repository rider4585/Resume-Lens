# Task list — Resume & JD Matcher

Use this list to track progress. Check off items as you complete them. The same tasks are tracked in Cursor’s task list for in-IDE progress.

---

## Legend

- [ ] Not started  
- [x] Done  
- [~] In progress / partial  

---

## 1. Project setup

- [x] Initialize git and add `.gitignore`
- [x] Create virtual environment and `requirements.txt`
- [x] Add config module (pydantic-settings) and `.env.example`
- [x] Create project skeleton (app, routers, services, schemas, prompts, tests, docs)
- [x] Verify app runs (`uvicorn app.main:app`) and health check responds

---

## 2. Document parser

- [x] Implement PDF extraction in `services/parser.py` (PyMuPDF)
- [x] Implement plain-text handling
- [x] Single entry point (e.g. `parse_resume`) with clear errors
- [x] Add parser tests (PDF, plain text, edge cases)

---

## 3. AI matcher (score + explanation)

- [x] Define prompts in `prompts/match.py` (system + user template, JSON output)
- [x] Implement `services/matcher.py` (OpenAI, structured output)
- [x] Add matcher tests with mocked OpenAI

---

## 4. API

- [x] Define Pydantic schemas (MatchRequest, MatchResponse)
- [x] Implement `POST /match` (and optional file upload)
- [x] Register router and add `GET /health`
- [x] Add API tests (success + validation)

---

## 5. Web UI

- [x] Add templates (index + result) and serve from FastAPI
- [x] Form: resume input (file/paste) + job description
- [x] Display score and explanation; handle errors
- [x] Optional: Tailwind or minimal CSS

---

## 6. CLI

- [x] Add Typer CLI (`cli.py`) with `match` command
- [x] Reuse matcher service; support file and stdin
- [x] Document in README

---

## 7. Bonus: Recommendations

- [x] Prompt and service for edit recommendations
- [x] `POST /api/recommendations` endpoint
- [x] UI: “Get recommendations” and display list

---

## 8. Bonus: Persistence & rankings

- [ ] SQLAlchemy models and DB setup (SQLite)
- [ ] Persist match on `POST /match`
- [ ] `GET /matches` and rankings/history page in UI

---

## 9. Polish & submission

- [ ] Full test run and Ruff
- [ ] README: architecture, tech decisions, AI rationale
- [ ] Update DECISIONS.md / IMPLEMENTATION.md if needed
- [ ] Submission: repo ready, runnable, presentable

---

## Quick reference: doc locations

| Doc | Purpose |
|-----|--------|
| `docs/DECISIONS.md` | All technology and architecture choices |
| `docs/IMPLEMENTATION.md` | Detailed step-by-step implementation |
| `docs/TASK_LIST.md` | This task list |

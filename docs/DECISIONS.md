# Project Decisions

This document records all architecture and technology choices for the **AI-Powered Resume & JD Matcher** project. Use it as the single source of truth for "why we built it this way."

---

## 1. Project overview

| Item | Choice |
|------|--------|
| **Name** | Resume & JD Matcher (ATS Checker) |
| **Objective** | Evaluate a candidate's resume against a job description and return a fit score with an explanation. |
| **Deliverables** | Working code (GitHub repo), README with architecture and AI rationale, presentable to a senior engineer. |

---

## 2. Technology stack

### 2.1 Core

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Language** | Python 3.11+ | Best ecosystem for PDF parsing, LLM APIs, and rapid iteration. |
| **API framework** | FastAPI | Async support, automatic OpenAPI docs, Pydantic validation, dependency injection. |
| **Validation & config** | Pydantic + pydantic-settings | Typed settings from env; consistent request/response contracts. |

### 2.2 Document processing

| Need | Choice | Rationale |
|------|--------|-----------|
| **PDF parsing** | PyMuPDF (fitz) | Reliable text extraction for resumes; good balance of speed and accuracy. |
| **Plain text** | Direct handling | No extra library; accept string or file upload. |

### 2.3 AI / LLM (local, no API cost)

| Need | Choice | Rationale |
|------|--------|-----------|
| **Primary model** | Ollama (local, e.g. llama3.2) | Free; runs on your machine; no API key. User has Ollama installed. |
| **Embeddings (RAG)** | Ollama `nomic-embed-text` | Local embeddings; chunk resume, retrieve top-k chunks by similarity to JD, augment prompt. Improves relevance. |
| **RAG pipeline** | Optional (`USE_RAG=true`) | Chunk resume → embed chunks and JD → cosine similarity → top-k resume excerpts → pass to LLM with full resume and JD. |
| **Output format** | JSON from prompt | Ollama has no native JSON mode; we ask for JSON in the prompt and extract it (including from \`\`\`json ... \`\`\` blocks). |
| **Prompt storage** | `app/prompts/match.py` | Versionable, testable; separate template when RAG is used (`USER_PROMPT_WITH_RAG_TEMPLATE`). |

### 2.4 Persistence (bonus)

| Need | Choice | Rationale |
|------|--------|-----------|
| **Database** | SQLite (MVP) | No setup; single file; sufficient for scores and rankings. |
| **ORM** | SQLAlchemy 2.0 | Clear schema; easy to migrate to PostgreSQL later by changing connection string. |
| **Schema** | Tables for resumes, job descriptions, matches (score, explanation, created_at) | Supports "persist scores and display rankings." |

### 2.5 Frontend

| Need | Choice | Rationale |
|------|--------|-----------|
| **UI** | Server-rendered HTML + minimal JS (or HTMX) | Fits "simple web UI"; no build step; maintainable. |
| **Styling** | Tailwind CSS (CDN) or minimal custom CSS | Quick, consistent styling without heavy front-end tooling. |

### 2.6 CLI

| Need | Choice | Rationale |
|------|--------|-----------|
| **CLI framework** | Typer | Typed CLI; reuses same core matching logic as the API. |

### 2.7 Quality & operations

| Need | Choice | Rationale |
|------|--------|-----------|
| **Testing** | pytest, pytest-asyncio, httpx | Test FastAPI; mock Ollama client for deterministic, fast tests. |
| **Linting / formatting** | Ruff | Single tool for lint and format; fast. |
| **Secrets** | python-dotenv + .env | Optional env (Ollama has no API key); .env for OLLAMA_BASE_URL etc. |
| **Deployment (optional)** | Docker | One-command run for reviewers. |

---

## 3. Architecture

### 3.1 High-level flow

```
Clients (Browser / CLI)
        │
        ▼
   FastAPI app
   • POST /match          → score + explanation
   • POST /recommendations → optional edits
   • GET  /matches        → optional rankings
        │
        ├──► Parser service (PDF + text)
        │
        └──► Matcher service
                  │
                  ├──► RAG (optional): Ollama embeddings → top-k resume chunks
                  ├──► Ollama (local LLM) → score + explanation
                  └──► Persistence (SQLAlchemy / SQLite)
```

### 3.2 Design principles

- **Stateless API** — no server-side session; each request has inputs and optional persistence.
- **Shared core** — one matching pipeline used by both API and CLI.
- **Config-driven** — model name, temperature, and prompt templates from config/env.
- **Layered** — ingestion (parser) → business logic (matcher) → API/CLI → persistence.

---

## 4. MVP vs bonus scope

| Scope | Items |
|-------|--------|
| **MVP** | Accept resume (text/PDF) + JD → AI score (0–100) + short justification → simple web UI or CLI. |
| **Bonus** | Recommend edits to improve match; persist scores and display rankings for multiple resumes. |

---

## 5. Out of scope (for now)

- Authentication / multi-tenancy  
- Multiple LLM providers in one run  
- Native mobile app  
- Real-time streaming of explanations  

---

## 6. Document history

| Date | Change |
|------|--------|
| (Initial) | Created; captured stack and architecture from planning. |

When you change a decision, add a new row here and update the section above.

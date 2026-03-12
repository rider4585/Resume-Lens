# Resume Lens — Installation & Setup

This guide walks you through installing and running **Resume Lens** (resume vs job description matcher) on your machine.

---

## Prerequisites

- **Python 3.9+** (3.10 or 3.11 recommended)
- **Node.js 18+** and **npm** (for the frontend)
- **Ollama** (local LLM; no API key required)
- **MySQL** (optional; default is SQLite)

---

## 1. Project setup

```bash
# Navigate to the project directory
cd "ATS Checker"
```

---

## 2. Backend (Python API)

### 2.1 Virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Environment variables

Copy the example env file and edit with your settings:

```bash
cp .env.example .env
```

Edit `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Chat model for matching | `llama3.2` |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model for RAG | `nomic-embed-text` |
| `USE_RAG` | Use RAG for matching | `true` |
| `DATABASE_URL` | Database connection (optional) | SQLite: `sqlite:///./matches.db` |

**Important:** Do not put literal `USERNAME` or `PASSWORD` in `DATABASE_URL`; use your real MySQL user and password. See [Database](#4-database-optional) below.

---

## 3. Ollama (local LLM)

Resume Lens uses **Ollama** for scoring and recommendations. No API key is needed.

### 3.1 Install Ollama

- **macOS / Linux:** [https://ollama.com](https://ollama.com) — download and install.
- Start Ollama (it may run as a service; otherwise run `ollama serve` in a terminal).

### 3.2 Pull required models

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

- `llama3.2` — used for match scoring, JD title generation, and recommendations.
- `nomic-embed-text` — used for RAG (resume chunk similarity) when `USE_RAG=true`.

---

## 4. Database (optional)

- **Default:** No config needed. The app uses **SQLite** and creates `matches.db` in the project root. You still need to run migrations once (see below).
- **MySQL (e.g. MAMP):** Use when you want a dedicated database.

### 4.1 Using SQLite (default)

1. Leave `DATABASE_URL` commented out in `.env`, or set:
   ```env
   DATABASE_URL=sqlite:///./matches.db
   ```
2. Run migrations (see [Section 5](#5-database-migrations)).

### 4.2 Using MySQL (e.g. MAMP)

1. Create the database (e.g. in phpMyAdmin or MySQL CLI):
   ```sql
   CREATE DATABASE resume_lens CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. In `.env`, set your real credentials (replace with your MySQL user and password):
   ```env
   DATABASE_URL=mysql+pymysql://YOUR_USER:YOUR_PASSWORD@127.0.0.1:8889/resume_lens
   ```
   For MAMP, the MySQL port is often **8889** (check MAMP’s MySQL port if different).

3. Run migrations (see [Section 5](#5-database-migrations)).

---

## 5. Database migrations

After setting `DATABASE_URL` (or using the default SQLite), run migrations from the **project root**:

```bash
# With venv activated
alembic upgrade head
```

This creates the tables: `saved_jds`, `resumes`, `matches`. For more commands, see [docs/MIGRATIONS.md](MIGRATIONS.md).

---

## 6. Frontend (React + Vite)

### 6.1 Install dependencies

```bash
cd frontend
npm install
cd ..
```

### 6.2 Development

From the project root, in a **separate terminal**:

```bash
cd frontend
npm run dev
```

The frontend runs at **http://localhost:8080** and proxies `/api` to the backend at `http://127.0.0.1:8000`.

### 6.3 Production build (optional)

```bash
cd frontend
npm run build
```

Serve the `frontend/dist` folder with your web server and point API requests to your backend URL.

---

## 7. Running the application

You need **two processes**: backend and frontend.

### Terminal 1 — Backend

```bash
cd "ATS Checker"
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000  
- API docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

### Terminal 2 — Frontend

```bash
cd "ATS Checker/frontend"
npm run dev
```

- App: http://localhost:8080  

Use the app in the browser; it will call the API via the dev-server proxy.

---

## 8. Verify setup

1. **Backend:** Open http://127.0.0.1:8000/health — should return `{"status":"ok"}`.
2. **Ollama:** Ensure `ollama list` shows `llama3.2` and `nomic-embed-text`.
3. **Frontend:** Open http://localhost:8080 — you should see the Resume Lens UI. Paste a short resume and JD and click **Compare** to test the full flow.

---

## 9. Optional

### CLI (no frontend)

From project root with venv activated:

```bash
python cli.py -r path/to/resume.pdf -j path/to/jd.txt
python cli.py -r resume.txt -j jd.txt --json
```

### Tests

```bash
pytest
```

### Storage

Saved JDs and resumes are stored under the `storage/` directory (created automatically). Pasted content is saved as `.txt` with line breaks and whitespace preserved; uploaded PDFs are stored as-is.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| `Access denied for user 'USERNAME'` | Replace `USERNAME` and `PASSWORD` in `.env` with your real MySQL credentials. |
| `Ollama request failed` | Install Ollama, run `ollama serve`, and run `ollama pull llama3.2` (and `nomic-embed-text` if using RAG). |
| `Provide job_description or jd_id` | Ensure the Compare request includes either pasted/uploaded JD text or a selected saved JD. |
| Frontend can’t reach API | Ensure the backend is running on port 8000 and the frontend dev server is using the proxy (`/api` → `http://127.0.0.1:8000` in `frontend/vite.config.ts`). |
| Migrations fail | Check `DATABASE_URL` in `.env`. For MySQL, ensure the database exists and the user has access. |

---

## Summary checklist

- [ ] Python 3.9+ venv created and `pip install -r requirements.txt` done  
- [ ] `.env` created from `.env.example` (no placeholder USERNAME/PASSWORD if using MySQL)  
- [ ] Ollama installed; `llama3.2` and `nomic-embed-text` pulled  
- [ ] Database: SQLite (default) or MySQL with `resume_lens` created and `DATABASE_URL` set  
- [ ] `alembic upgrade head` run from project root  
- [ ] `frontend/npm install` and `npm run dev` (frontend on 8080)  
- [ ] `uvicorn app.main:app --reload` (backend on 8000)  
- [ ] http://localhost:8080 opens and Compare works  

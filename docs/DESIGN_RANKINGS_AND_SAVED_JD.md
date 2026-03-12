# Design: Saved JDs, Resume–JD Relation, Rankings (MySQL)

This document captures the design for saving JDs, mapping one JD to multiple resumes, and ranking, with MySQL and security/scalability considerations.

---

## 1. User flow (UI)

1. **JD input options (match form)**  
   User can provide the job description in one of three ways:
   - **Paste** text in a textarea.
   - **Upload** a file (PDF or text).
   - **Choose from saved JDs** (dropdown populated from DB).

2. **Checkbox: “Save JD for future use to rank resumes”**  
   - If checked: after a successful match, we persist the JD (if not already saved) and the match (JD ↔ resume).  
   - If user **selected a saved JD** from the dropdown: we always persist the match (resume ↔ that JD).  
   So **JD → multiple resumes** exists only when:
   - User selected an already saved JD, or  
   - User checked “Save JD for future use to rank resumes” (and we save the JD + match).

3. **Saved JDs management**  
   - Dedicated UI area: list of saved JDs (title, date).  
   - User can **add** a new saved JD by paste or file upload (without running a match).  
   - User can **select** a saved JD to (a) use in the match form, or (b) open the **Rankings** view for that JD.  
   - **On click of a saved JD:** user can **view** the JD in the same format it was saved (see §2.3).

4. **Rankings area (dedicated)**  
   - When user selects a saved JD, show a dedicated Rankings area: "Resumes compared against this JD" — a single list/table of all resumes matched to that JD.  
   - Resumes are **already sorted best to worst** (score descending; ties by date). Columns: rank #, resume label, score, date, explanation, and a **View** action. On click of a resume (or "View"), user can **view** that resume in the same format it was saved (see §2.3).

---

## 2. Data model (MySQL)

### 2.1 Tables

- **saved_jds** (job descriptions we save for reuse and ranking)  
  - `id` — PK, auto-increment (internal).  
  - `uuid` — unique, non-readable public id (e.g. UUID4). Used in API/URLs so we don’t expose sequential IDs.  
  - `title` — short label (e.g. first line of JD or “Frontend Engineer (React)”).  
  - `content_text` — full JD text (used for matching and display).  
  - `original_filename` — if JD was uploaded from file, store the real filename here; else NULL for paste.  
  - `file_extension` — `'pdf' | 'txt'`; used with `uuid` to serve file from `storage/jds/{uuid}.{file_extension}`.  
  - `source` — `'paste' | 'file_upload'`.  
  - `created_at` — timestamp.

- **resumes** (one row per “resume instance” we use in matches)  
  - `id` — PK.  
  - `uuid` — unique, non-readable public id (UUID4).  
  - `resume_text` — extracted or pasted text (for matching).  
  - `original_filename` — if from file upload, real filename; else NULL (e.g. “Pasted resume”).  
  - `file_extension` — `'pdf' | 'txt'`; used with `uuid` to serve file from `storage/resumes/{uuid}.{file_extension}`.  
  - `created_at` — timestamp.

- **matches** (one row per “resume matched to JD” when we persist)  
  - `id` — PK.  
  - `job_description_id` — FK → `saved_jds.id`.  
  - `resume_id` — FK → `resumes.id`.  
  - `score` — integer 0–100.  
  - `explanation` — text.  
  - `created_at` — timestamp.  

Relation: **one saved_jd → many matches → many resumes**. So one JD can have many resumes ranked by score.

### 2.2 File handling and storage (JD / Resume)

All stored content is kept on the **filesystem** under a configurable storage root (e.g. `storage/`), keyed by **uuid**. The DB stores metadata and extracted or pasted **text** for matching; it does **not** store raw file bytes.

- **Pasted JD or pasted resume (text only):**  
  - Save a **.txt file** on the filesystem at e.g. `storage/jds/{uuid}.txt` or `storage/resumes/{uuid}.txt`.  
  - Write the **exact** pasted string (all whitespace and line breaks preserved).  
  - In DB: `content_text` / `resume_text` = same text; `source` = `'paste'`; `file_extension` = `'txt'`.

- **Uploaded JD (PDF or .txt file):**  
  - Save the **actual file** on the filesystem as `storage/jds/{uuid}.pdf` or `storage/jds/{uuid}.txt`.  
  - Extract text and store in `saved_jds.content_text` for matching.  
  - In DB: `original_filename`, `file_extension`, `source` = `'file_upload'`.

- **Uploaded resume (PDF or .txt file):**  
  - Save the **actual file** on the filesystem as `storage/resumes/{uuid}.pdf` or `storage/resumes/{uuid}.txt`.  
  - Extract text for matching and store in `resumes.resume_text`.  
  - In DB: `original_filename`, `file_extension`.

**View** uses the stored file (PDF or .txt) so the user sees the asset in the same format it was uploaded or pasted (pasted = .txt with exact whitespace/line breaks).

### 2.3 View endpoints (serve stored file)

- **GET /api/jds/{uuid}/file** — serve the stored JD file (PDF or .txt) with correct `Content-Type` and `Content-Disposition` (e.g. inline or download with original filename if available).  
- **GET /api/resumes/{uuid}/file** — serve the stored resume file (PDF or .txt) with correct `Content-Type` and `Content-Disposition**.

DB: add **saved_jds** and **resumes** columns `file_extension` (e.g. `'pdf' | 'txt'`) or `stored_path` so the API can locate the file on disk and set the right response headers.

---

## 3. API (summary)

- **POST /api/match** (JSON)  
  - Body: `resume_text`, `job_description`; optional: `jd_id` (uuid of saved JD), `save_jd` (bool), `resume_label`.  
  - If `jd_id` present: load JD from `saved_jds` by uuid, use `content_text` for matching.  
  - If `save_jd` true and JD text provided: create or reuse `saved_jds` row (uuid, title from first line, content_text, source=’paste’).  
  - After match: if we have a saved JD (from `jd_id` or just created) and we’re persisting, create/find `resumes` row (uuid, resume_text, original_filename=resume_label or null), then create `matches` row.

- **POST /api/match/upload** (multipart)  
  - Same idea: optional `jd_id`, `save_jd`; resume from file (we have filename + extracted text).  
  - Persist match when “saved JD” path is chosen; resume row uses `original_filename` from uploaded file.

- **GET /api/jds**  
  - List saved JDs: e.g. `{ uuid, title, created_at }` for dropdown. Pagination optional.

- **POST /api/jds** (optional, for “Add saved JD” without matching)  
  - Body: paste text or multipart file. Creates `saved_jds` row; returns uuid, title.

- **GET /api/matches?jd_id=:uuid**  
  - Matches for that JD; response includes resume label (original_filename or “Pasted resume”), score, explanation, created_at.  
  - Ordered by **score DESC**, then created_at DESC. Pagination optional.

- **GET /api/jds/:uuid** (optional)  
  - Return one JD (title, content_text) for “view/edit” or prefill.

---

## 4. Security

- **Non-readable references:** Use **uuid** (e.g. UUID4) for all public identifiers (saved_jds, resumes). Use these in URLs and API; avoid exposing sequential `id` in URLs to reduce enumeration and information leakage.
- **No raw files in DB:** Store only extracted text (and metadata). Reduces attack surface and size; no need to serve or parse stored binaries.
- **Original filename:** Store only for display; never use it for path or execution. Sanitize on input (e.g. strip path, limit length, allowed charset).
- **Upload validation:** Limit file size (e.g. 5–10 MB); allow only PDF and plain text; validate content type and magic bytes where possible.
- **Input length:** Cap length of pasted JD and resume text (e.g. 50k–100k chars) to avoid abuse.
- **Future:** Rate limiting, auth for “save”/“rankings” if needed.

---

## 5. Scalability

- **MySQL:** Use MySQL as requested; connection string in config (e.g. `DATABASE_URL=mysql+pymysql://user:pass@host/dbname`). Indexes:
  - `saved_jds(uuid)` unique.
  - `resumes(uuid)` unique.
  - `matches(job_description_id)`, `matches(resume_id)`, `matches(score)` (for ranking and filters).
- **No large blobs:** Store only text for JD and resume; no PDF/blob columns. Keeps rows small and queries fast.
- **Connection pooling:** Use SQLAlchemy pool (default is fine to start; tune later if needed).
- **Pagination:** Support `limit`/`offset` or `page`/`page_size` on GET /api/jds and GET /api/matches.
- **Optional later:** Read replica for GETs; separate file store (e.g. S3) keyed by uuid if we ever need to store actual files.

---

## 6. Optional enhancements (later)

- **Deduplication:** For “same JD + same resume text” we could upsert one match (e.g. by hash of resume_text + jd_id) to avoid duplicate rows.  
- **Soft delete:** Add `deleted_at` on saved_jds/resumes if we want “delete” without hard delete.  
- **Auth:** If the app gets multiple tenants, add user/tenant id to saved_jds, resumes, matches and scope all queries.

---

## 7. Implementation order

1. **Config:** Add MySQL `DATABASE_URL`; keep SQLite as optional fallback for local dev if desired.  
2. **Models:** SQLAlchemy models for `saved_jds`, `resumes`, `matches` (with uuid, FKs, indexes).  
3. **DB init:** Create tables (e.g. on startup or migration); ensure uuid generated on insert.  
4. **APIs:** Implement POST /api/jds (create saved JD), GET /api/jds (list), GET /api/matches?jd_id=; adjust POST /api/match and POST /api/match/upload to accept jd_id/save_jd and persist when applicable.  
5. **UI:** Match form: JD input = paste | upload file | select saved JD; checkbox “Save JD for future use to rank resumes”; after match, if save or saved JD used, show “Saved” or redirect to rankings.  
6. **UI:** Saved JDs list + “Rankings for this JD” view (table: resume label, score, date, explanation).

If this aligns with your intent (save JD option, choose from saved JD, JD → many resumes only when saved/saved JD used, MySQL, uuid + original_filename, text-only storage for scalability and security), next step is implementing the models and APIs in the codebase.

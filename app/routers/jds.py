"""Saved JDs: list, create (paste/file), serve file, list matches (rankings) for a JD."""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.match import Match, Resume, SavedJD
from app.services import parser
from app.services.storage import get_jd_path, get_resume_path, ensure_storage_dirs, save_jd_file, save_jd_pasted

router = APIRouter()


def _jd_title_from_text(text: str) -> str:
    line = (text.strip().split("\n") or [""])[0].strip() or "Job description"
    return line[:80] if len(line) > 80 else line


def _file_extension_from_filename(filename: Optional[str]) -> str:
    if not filename or not filename.lower().endswith(".pdf"):
        return "txt"
    return "pdf"


@router.get("/jds")
def list_jds(db: Session = Depends(get_db)):
    """List saved JDs in career-compass shape: id, title, company, savedAt, snippet, content, comparisons."""
    rows = db.query(SavedJD).order_by(desc(SavedJD.created_at)).all()
    out = []
    for r in rows:
        matches = (
            db.query(Match)
            .filter(Match.job_description_id == r.id)
            .order_by(desc(Match.score), desc(Match.created_at))
            .all()
        )
        comparisons = [
            {
                "resumeName": m.resume.original_filename or "Pasted resume",
                "resumeUuid": m.resume.uuid,
                "score": m.score,
                "comparedAt": m.created_at.strftime("%Y-%m-%d") if m.created_at else "",
            }
            for m in matches
        ]
        content = r.content_text or ""
        snippet = (content[:120] + "…") if len(content) > 120 else content
        out.append({
            "id": r.uuid,
            "title": r.title,
            "company": "",
            "savedAt": r.created_at.strftime("%Y-%m-%d") if r.created_at else "",
            "snippet": snippet,
            "content": content,
            "comparisons": comparisons,
        })
    return out


@router.post("/jds")
async def create_jd(
    job_description: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Create a saved JD from pasted text or uploaded file (PDF or .txt). Returns { uuid, title }."""
    ensure_storage_dirs()
    if jd_file and jd_file.filename:
        content = await jd_file.read()
        if jd_file.filename.lower().endswith(".pdf"):
            jd_text = parser.parse_resume(content=content, content_type="application/pdf")
        else:
            jd_text = parser.parse_resume(content=content)
        title = _jd_title_from_text(jd_text)
        ext = _file_extension_from_filename(jd_file.filename)
        jd = SavedJD(
            title=title,
            content_text=jd_text.strip(),
            original_filename=jd_file.filename,
            file_extension=ext,
            source="file_upload",
        )
        db.add(jd)
        db.flush()
        save_jd_file(jd.uuid, content, ext)
        db.commit()
        db.refresh(jd)
        return {"uuid": jd.uuid, "title": jd.title}
    if job_description and job_description.strip():
        raw = job_description
        title = _jd_title_from_text(raw)
        jd = SavedJD(
            title=title,
            content_text=raw.strip(),
            original_filename=None,
            file_extension="txt",
            source="paste",
        )
        db.add(jd)
        db.flush()
        save_jd_pasted(jd.uuid, raw)
        db.commit()
        db.refresh(jd)
        return {"uuid": jd.uuid, "title": jd.title}
    raise HTTPException(status_code=422, detail="Provide job_description (paste) or jd_file (upload)")


@router.get("/jds/{jd_uuid}")
def get_jd(jd_uuid: str, db: Session = Depends(get_db)):
    """Return one JD (title, content_text) for display or recommendations."""
    jd = db.query(SavedJD).filter(SavedJD.uuid == jd_uuid).first()
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")
    return {"uuid": jd.uuid, "title": jd.title, "content_text": jd.content_text}


@router.get("/jds/{jd_uuid}/file")
def get_jd_file(jd_uuid: str, db: Session = Depends(get_db)):
    """Serve the stored JD file (PDF or .txt) with correct Content-Type."""
    jd = db.query(SavedJD).filter(SavedJD.uuid == jd_uuid).first()
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")
    path = get_jd_path(jd.uuid, jd.file_extension)
    if not path.exists():
        raise HTTPException(status_code=404, detail="JD file not found")
    media_type = "application/pdf" if jd.file_extension.lower() == "pdf" else "text/plain"
    filename = jd.original_filename or f"jd.{jd.file_extension}"
    return FileResponse(
        path,
        media_type=media_type,
        filename=filename,
        content_disposition_type="inline",
    )


@router.get("/jds/{jd_uuid}/matches")
def get_jd_matches(jd_uuid: str, db: Session = Depends(get_db)):
    """Rankings for this JD: resumes compared against this JD, sorted best to worst (score desc)."""
    jd = db.query(SavedJD).filter(SavedJD.uuid == jd_uuid).first()
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")
    matches = (
        db.query(Match)
        .filter(Match.job_description_id == jd.id)
        .order_by(desc(Match.score), desc(Match.created_at))
        .all()
    )
    out = []
    for rank, m in enumerate(matches, start=1):
        resume = m.resume
        label = resume.original_filename or "Pasted resume"
        out.append({
            "rank": rank,
            "resume_uuid": resume.uuid,
            "resume_label": label,
            "score": m.score,
            "explanation": m.explanation,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
    return out


@router.get("/resumes/{resume_uuid}/file")
def get_resume_file(resume_uuid: str, db: Session = Depends(get_db)):
    """Serve the stored resume file (PDF or .txt) with correct Content-Type."""
    resume = db.query(Resume).filter(Resume.uuid == resume_uuid).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    path = get_resume_path(resume.uuid, resume.file_extension)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Resume file not found")
    media_type = "application/pdf" if resume.file_extension.lower() == "pdf" else "text/plain"
    filename = resume.original_filename or f"resume.{resume.file_extension}"
    return FileResponse(
        path,
        media_type=media_type,
        filename=filename,
        content_disposition_type="inline",
    )

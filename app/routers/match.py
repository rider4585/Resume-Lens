"""Match router: resume vs job description; optional persist to saved JD and rankings."""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.match import Match, Resume, SavedJD
from app.schemas.match import MatchRequest, MatchResponse, MatchScoreItem
from app.services import matcher, parser
from app.services.jd_title import generate_jd_title
from app.services.storage import (
    ensure_storage_dirs,
    save_jd_file,
    save_jd_pasted,
    save_resume_file,
    save_resume_pasted,
)

router = APIRouter()


def _jd_title_from_text(text: str) -> str:
    """First line or first 80 chars for JD title."""
    line = (text.strip().split("\n") or [""])[0].strip() or "Job description"
    return line[:80] if len(line) > 80 else line


def _file_extension_from_filename(filename: Optional[str]) -> str:
    if not filename:
        return "txt"
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    return "txt"


def _match(resume_text: str, job_description: str, include_resume_text: bool = False) -> dict:
    """Run matcher; return dict with score, summary, strengths, weaknesses."""
    resume_text = (resume_text or "").strip()
    if not resume_text:
        raise HTTPException(status_code=422, detail="resume_text is required and cannot be empty")
    job_description = (job_description or "").strip()
    if not job_description:
        raise HTTPException(status_code=422, detail="job_description is required and cannot be empty")
    try:
        result = matcher.match_resume_to_jd(resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    out = dict(result)
    out["resume_text"] = resume_text if include_resume_text else None
    return out


@router.post("/match", response_model=MatchResponse)
def match_endpoint(request: MatchRequest, db: Session = Depends(get_db)) -> MatchResponse:
    """Score resume against job description (JSON). Optionally use saved JD and/or save JD and persist match."""
    ensure_storage_dirs()
    job_description = (request.job_description or "").strip()
    jd = None
    if request.jd_id:
        jd = db.query(SavedJD).filter(SavedJD.uuid == request.jd_id).first()
        if not jd:
            raise HTTPException(status_code=404, detail="Saved JD not found")
        job_description = jd.content_text
    if not job_description:
        raise HTTPException(status_code=422, detail="Provide job_description or jd_id")

    # Optionally create and save new JD (exact text for storage)
    if request.save_jd and not request.jd_id and request.job_description:
        raw_jd = request.job_description  # exact for file
        title = generate_jd_title(raw_jd) or _jd_title_from_text(raw_jd)
        jd = SavedJD(
            title=title,
            content_text=raw_jd.strip(),
            original_filename=None,
            file_extension="txt",
            source="paste",
        )
        db.add(jd)
        db.flush()
        save_jd_pasted(jd.uuid, raw_jd)
        db.commit()
        db.refresh(jd)

    resume_text_for_match = (request.resume_text or "").strip()
    raw_resume = request.resume_text or ""  # exact for storage when persisting
    result = _match(resume_text_for_match, job_description, include_resume_text=True)

    # Persist match when we have a saved JD (from jd_id or just created)
    if jd:
        resume = Resume(
            resume_text=resume_text_for_match,
            original_filename=request.resume_label,
            file_extension="txt",
        )
        db.add(resume)
        db.flush()
        save_resume_pasted(resume.uuid, raw_resume)
        match_row = Match(
            job_description_id=jd.id,
            resume_id=resume.id,
            score=result["score"],
            explanation=result.get("summary") or "",
        )
        db.add(match_row)
        db.commit()

    return MatchResponse(
        score=result["score"],
        summary=result["summary"],
        strengths=[MatchScoreItem(**s) for s in result.get("strengths", [])],
        weaknesses=[MatchScoreItem(**w) for w in result.get("weaknesses", [])],
        resume_text=result.get("resume_text"),
        jd_uuid=jd.uuid if jd else None,
    )


@router.post("/match/upload", response_model=MatchResponse)
async def match_upload_endpoint(
    resume_file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    jd_id: Optional[str] = Form(None),
    save_jd: bool = Form(False),
    db: Session = Depends(get_db),
) -> MatchResponse:
    """Score resume file (PDF or text) against job description (paste, file, or saved JD). Optionally save JD and persist."""
    ensure_storage_dirs()
    content = await resume_file.read()
    content_type = resume_file.content_type or ""
    if resume_file.filename and resume_file.filename.lower().endswith(".pdf"):
        resume_text = parser.parse_resume(content=content, content_type="application/pdf")
    else:
        resume_text = parser.parse_resume(content=content)

    jd = None
    jd_text = ""
    if jd_id:
        jd = db.query(SavedJD).filter(SavedJD.uuid == jd_id).first()
        if not jd:
            raise HTTPException(status_code=404, detail="Saved JD not found")
        jd_text = jd.content_text
    elif jd_file and jd_file.filename:
        jd_content = await jd_file.read()
        if jd_file.filename.lower().endswith(".pdf"):
            jd_text = parser.parse_resume(content=jd_content, content_type="application/pdf")
        else:
            jd_text = parser.parse_resume(content=jd_content)
        if save_jd:
            title = generate_jd_title(jd_text) or _jd_title_from_text(jd_text)
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
            save_jd_file(jd.uuid, jd_content, ext)
            db.commit()
            db.refresh(jd)
    elif job_description:
        jd_text = job_description.strip()
        if save_jd and jd_text:
            raw_jd = job_description  # exact for file
            title = generate_jd_title(raw_jd) or _jd_title_from_text(raw_jd)
            jd = SavedJD(
                title=title,
                content_text=jd_text,
                original_filename=None,
                file_extension="txt",
                source="paste",
            )
            db.add(jd)
            db.flush()
            save_jd_pasted(jd.uuid, raw_jd)
            db.commit()
            db.refresh(jd)
    if not jd_text.strip():
        raise HTTPException(status_code=422, detail="Provide job description (paste, upload JD file, or choose saved JD)")

    result = _match(resume_text, jd_text, include_resume_text=True)

    if jd:
        ext = _file_extension_from_filename(resume_file.filename)
        resume = Resume(
            resume_text=resume_text,
            original_filename=resume_file.filename,
            file_extension=ext,
        )
        db.add(resume)
        db.flush()
        save_resume_file(resume.uuid, content, ext)
        match_row = Match(
            job_description_id=jd.id,
            resume_id=resume.id,
            score=result["score"],
            explanation=result.get("summary") or "",
        )
        db.add(match_row)
        db.commit()

    return MatchResponse(
        score=result["score"],
        summary=result["summary"],
        strengths=[MatchScoreItem(**s) for s in result.get("strengths", [])],
        weaknesses=[MatchScoreItem(**w) for w in result.get("weaknesses", [])],
        resume_text=result.get("resume_text"),
        jd_uuid=jd.uuid if jd else None,
    )

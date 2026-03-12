"""Filesystem storage for saved JDs and resumes (by uuid)."""

from pathlib import Path
from typing import Literal

from app.config import get_settings

Extension = Literal["pdf", "txt"]


def _root() -> Path:
    return Path(get_settings().storage_root)


def _jds_dir() -> Path:
    d = _root() / "jds"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _resumes_dir() -> Path:
    d = _root() / "resumes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure_storage_dirs() -> None:
    """Create storage/jds and storage/resumes if they do not exist."""
    _jds_dir()
    _resumes_dir()


def save_jd_pasted(jd_uuid: str, exact_text: str) -> Path:
    """Write pasted JD as .txt with exact whitespace and line breaks. Returns path."""
    path = _jds_dir() / f"{jd_uuid}.txt"
    path.write_text(exact_text, encoding="utf-8")
    return path


def save_jd_file(jd_uuid: str, content: bytes, extension: Extension) -> Path:
    """Write uploaded JD file (PDF or .txt). Returns path."""
    path = _jds_dir() / f"{jd_uuid}.{extension}"
    path.write_bytes(content)
    return path


def save_resume_pasted(resume_uuid: str, exact_text: str) -> Path:
    """Write pasted resume as .txt with exact whitespace and line breaks. Returns path."""
    path = _resumes_dir() / f"{resume_uuid}.txt"
    path.write_text(exact_text, encoding="utf-8")
    return path


def save_resume_file(resume_uuid: str, content: bytes, extension: Extension) -> Path:
    """Write uploaded resume file (PDF or .txt). Returns path."""
    path = _resumes_dir() / f"{resume_uuid}.{extension}"
    path.write_bytes(content)
    return path


def get_jd_path(jd_uuid: str, file_extension: str) -> Path:
    """Return path to stored JD file. Caller should check exists."""
    return _jds_dir() / f"{jd_uuid}.{file_extension}"


def get_resume_path(resume_uuid: str, file_extension: str) -> Path:
    """Return path to stored resume file. Caller should check exists."""
    return _resumes_dir() / f"{resume_uuid}.{file_extension}"

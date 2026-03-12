"""ORM models: saved JDs, resumes, matches."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db import Base


def _uuid4_str() -> str:
    return str(uuid.uuid4())


class SavedJD(Base):
    """Saved job description for reuse and ranking."""

    __tablename__ = "saved_jds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=_uuid4_str)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_extension: Mapped[str] = mapped_column(String(10), nullable=False, default="txt")
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # 'paste' | 'file_upload'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matches: Mapped[list["Match"]] = relationship("Match", back_populates="job_description")


class Resume(Base):
    """One resume instance used in matches."""

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=_uuid4_str)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_extension: Mapped[str] = mapped_column(String(10), nullable=False, default="txt")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matches: Mapped[list["Match"]] = relationship("Match", back_populates="resume")


class Match(Base):
    """One resume matched to one JD (score and explanation)."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_description_id: Mapped[int] = mapped_column(ForeignKey("saved_jds.id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job_description: Mapped["SavedJD"] = relationship("SavedJD", back_populates="matches")
    resume: Mapped["Resume"] = relationship("Resume", back_populates="matches")

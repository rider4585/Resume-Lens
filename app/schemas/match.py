"""Match request and response schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class MatchScoreItem(BaseModel):
    title: str
    description: str
    score: int = Field(..., ge=0, le=100)


class MatchRequest(BaseModel):
    """Input for resume vs job description match."""

    resume_text: Optional[str] = Field(None, description="Resume content as plain text")
    job_description: Optional[str] = Field(None, description="Job description text (required if jd_id not set)")
    jd_id: Optional[str] = Field(None, description="UUID of saved JD to use instead of job_description")
    save_jd: bool = Field(False, description="Save JD for future use to rank resumes")
    resume_label: Optional[str] = Field(None, description="Label for resume in rankings (e.g. filename)")


class MatchResponse(BaseModel):
    """Result of matching resume to job description (JSON for frontend)."""

    score: int = Field(..., ge=0, le=100, description="Fit score 0-100")
    summary: str = Field(..., description="Overall fit summary")
    strengths: List[MatchScoreItem] = Field(default_factory=list, description="Strengths with scores")
    weaknesses: List[MatchScoreItem] = Field(default_factory=list, description="Weaknesses/gaps with scores")
    resume_text: Optional[str] = Field(None, description="Resume text for recommendations")
    jd_uuid: Optional[str] = Field(None, description="UUID of saved JD when match was persisted")
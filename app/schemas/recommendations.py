"""Recommendations request and response schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendationsRequest(BaseModel):
    """Input for getting resume improvement recommendations."""

    resume_text: Optional[str] = Field(None, description="Resume content as plain text")
    job_description: str = Field(..., min_length=1, description="Job description text")
    score: Optional[int] = Field(None, ge=0, le=100, description="Current match score (if omitted, match is run first)")
    explanation: Optional[str] = Field(None, description="Current match explanation (if omitted, match is run first)")


class RecommendationsResponse(BaseModel):
    """List of recommended resume edits."""

    recommendations: List[str] = Field(..., description="Concrete edits to improve match")

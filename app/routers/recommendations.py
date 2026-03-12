"""Recommendations router: suggest resume edits to improve match."""

from fastapi import APIRouter, HTTPException

from app.schemas.recommendations import RecommendationsRequest, RecommendationsResponse
from app.services import matcher, recommendations

router = APIRouter()


@router.post("/recommendations", response_model=RecommendationsResponse)
def post_recommendations(request: RecommendationsRequest) -> RecommendationsResponse:
    """
    Get 3-5 concrete resume edits to improve match with the job description.
    If score/explanation are not provided, runs the matcher first to get them.
    """
    resume_text = (request.resume_text or "").strip()
    if not resume_text:
        raise HTTPException(
            status_code=422,
            detail="resume_text is required and cannot be empty",
        )
    job_description = (request.job_description or "").strip()
    if not job_description:
        raise HTTPException(
            status_code=422,
            detail="job_description is required and cannot be empty",
        )

    score = request.score
    explanation = request.explanation or ""
    if score is None:
        try:
            match_result = matcher.match_resume_to_jd(resume_text, job_description)
            score = match_result["score"]
            explanation = match_result["explanation"]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        recs = recommendations.get_recommendations(
            resume_text, job_description, int(score), explanation
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendations failed: {type(e).__name__}: {e}",
        ) from e

    return RecommendationsResponse(recommendations=recs or [])

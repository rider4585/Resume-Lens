"""Tests for match API endpoint."""

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from tests.conftest import client


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    """Health endpoint returns 200."""
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_root_serves_html(client: AsyncClient):
    """Root serves the web UI (HTML)."""
    r = await client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    assert "Resume" in r.text and "JD Matcher" in r.text


@pytest.mark.asyncio
async def test_match_requires_job_description(client: AsyncClient):
    """POST /api/match without job_description returns 422."""
    r = await client.post("/api/match", json={"resume_text": "I am a developer."})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_match_requires_resume_text(client: AsyncClient):
    """POST /api/match with empty resume_text returns 422."""
    r = await client.post(
        "/api/match",
        json={"resume_text": "   ", "job_description": "We need a developer."},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_match_success_returns_score_and_explanation(client: AsyncClient):
    """POST /api/match with valid body returns 200 and MatchResponse when matcher is mocked."""
    with patch("app.routers.match.matcher.match_resume_to_jd") as mock_match:
        mock_match.return_value = {"score": 70, "explanation": "Good fit for backend role."}

        r = await client.post(
            "/api/match",
            json={
                "resume_text": "Senior Python developer with 5 years experience.",
                "job_description": "We need a Python backend engineer.",
            },
        )

    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 70
    assert data["explanation"] == "Good fit for backend role."


@pytest.mark.asyncio
async def test_match_matcher_value_error_returns_400(client: AsyncClient):
    """When matcher raises ValueError, API returns 400."""
    with patch("app.routers.match.matcher.match_resume_to_jd") as mock_match:
        mock_match.side_effect = ValueError("Ollama request failed.")

        r = await client.post(
            "/api/match",
            json={
                "resume_text": "Resume text.",
                "job_description": "Job description.",
            },
        )

    assert r.status_code == 400
    assert "Ollama" in r.json().get("detail", "")

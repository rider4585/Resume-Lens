"""Tests for AI matcher (Ollama + optional RAG)."""

from unittest.mock import MagicMock, patch

import pytest

from app.services import matcher


def test_match_resume_to_jd_returns_score_and_explanation():
    """Matcher returns dict with score 0-100 and explanation when Ollama is mocked."""
    fake_response = {
        "message": {
            "content": '{"score": 75, "explanation": "Strong backend experience but lacks cloud skills."}'
        }
    }

    with patch("ollama.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.chat.return_value = fake_response
        mock_client_class.return_value = mock_client

        with patch("app.services.matcher.get_settings") as mock_settings:
            mock_settings.return_value.ollama_base_url = "http://localhost:11434"
            mock_settings.return_value.ollama_model = "llama3.2"
            mock_settings.return_value.ollama_embedding_model = "nomic-embed-text"
            mock_settings.return_value.use_rag = False

            result = matcher.match_resume_to_jd(
                "Senior Python developer, 5 years experience.",
                "We need a Python backend engineer with AWS.",
            )

    assert result["score"] == 75
    assert "backend" in result["explanation"].lower() or "cloud" in result["explanation"].lower()


def test_match_resume_to_jd_extracts_json_from_markdown():
    """Matcher extracts JSON when model wraps it in ```json ... ```."""
    fake_response = {
        "message": {
            "content": 'Here is the result:\n```json\n{"score": 60, "explanation": "Partial fit."}\n```'
        }
    }

    with patch("ollama.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.chat.return_value = fake_response
        mock_client_class.return_value = mock_client

        with patch("app.services.matcher.get_settings") as mock_settings:
            mock_settings.return_value.ollama_base_url = "http://localhost:11434"
            mock_settings.return_value.ollama_model = "llama3.2"
            mock_settings.return_value.ollama_embedding_model = "nomic-embed-text"
            mock_settings.return_value.use_rag = False

            result = matcher.match_resume_to_jd("resume", "jd")

    assert result["score"] == 60
    assert result["explanation"] == "Partial fit."


def test_match_resume_to_jd_empty_input_raises():
    """Matcher raises ValueError when resume or JD is empty."""
    with pytest.raises(ValueError, match="required"):
        matcher.match_resume_to_jd("", "some jd")
    with pytest.raises(ValueError, match="required"):
        matcher.match_resume_to_jd("resume", "")
    with pytest.raises(ValueError, match="required"):
        matcher.match_resume_to_jd("   ", "jd")

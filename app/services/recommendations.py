"""Recommendations service: suggest resume edits to improve match (Ollama)."""

import json
import re
from typing import List

from app.config import get_settings


def _extract_json(raw: str) -> str:
    """Extract JSON from model output (handle markdown code blocks)."""
    raw = (raw or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        return m.group(1).strip()
    return raw


def get_recommendations(
    resume_text: str,
    job_description: str,
    score: int,
    explanation: str,
) -> List[str]:
    """
    Call Ollama to get 3-5 concrete resume edits to improve match.
    :return: List of recommendation strings.
    :raises ValueError: If Ollama fails or response is invalid.
    """
    settings = get_settings()
    host = settings.ollama_base_url
    model = settings.ollama_model

    from app.prompts.recommendations import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

    resume_safe = (resume_text or "")[:5000].replace("{", "{{").replace("}", "}}")
    jd_safe = (job_description or "")[:3000].replace("{", "{{").replace("}", "}}")
    expl_safe = (explanation or "No explanation provided.").replace("{", "{{").replace("}", "}}")
    user_content = USER_PROMPT_TEMPLATE.format(
        score=score,
        explanation=expl_safe,
        resume_text=resume_safe,
        job_description=jd_safe,
    )

    try:
        from ollama import Client
    except ImportError:
        raise ValueError(
            "Ollama Python package is required. Install with: pip install ollama"
        ) from None

    client = Client(host=host)
    try:
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            options={"temperature": 0.4},
        )
    except Exception as e:
        raise ValueError(
            f"Ollama request failed (is Ollama running and model '{model}' pulled?): {e}"
        ) from e

    raw = _get_content(response)
    if not raw:
        raise ValueError("Empty response from Ollama")

    json_str = _extract_json(raw)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("Model did not return a JSON object")

    recs = data.get("recommendations")
    if recs is None:
        raise ValueError("Model response must include 'recommendations'")
    if not isinstance(recs, list):
        recs = [str(recs)] if recs else []
    return [str(r).strip() for r in recs if r]


def _get_content(response):
    """Extract content from Ollama chat response (dict or object)."""
    if response is None:
        return None
    try:
        if isinstance(response, dict):
            msg = response.get("message")
            return (msg.get("content") if isinstance(msg, dict) else None) or None
        msg = getattr(response, "message", None)
        if msg is None:
            return None
        if isinstance(msg, dict):
            return msg.get("content")
        return getattr(msg, "content", None)
    except Exception:
        return None

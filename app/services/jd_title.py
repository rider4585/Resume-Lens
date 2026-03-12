"""Generate a short, descriptive title for a job description using the LLM."""

from typing import Optional

from app.config import get_settings

PROMPT = """Based on the job description below, reply with a single short title (e.g. "Senior Frontend Developer - React, TypeScript" or "Data Scientist - ML/NLP"). One line only, no quotes, no prefix. Maximum 80 characters."""


def generate_jd_title(job_description: str) -> Optional[str]:
    """
    Use Ollama to generate a concise title for the job description.
    Returns None on failure so caller can fall back to first-line title.
    """
    jd = (job_description or "").strip()
    if not jd:
        return None
    jd_safe = jd[:4000].replace("{", "{{").replace("}", "}}")
    settings = get_settings()
    try:
        from ollama import Client
    except ImportError:
        return None
    client = Client(host=settings.ollama_base_url)
    try:
        response = client.chat(
            model=settings.ollama_model,
            messages=[{"role": "user", "content": f"{PROMPT}\n\n{jd_safe}"}],
            options={"temperature": 0.3},
        )
    except Exception:
        return None
    content = _get_content(response)
    if not content:
        return None
    title = content.strip().split("\n")[0].strip()
    if len(title) > 80:
        title = title[:80].rstrip()
    return title if title else None


def _get_content(response) -> Optional[str]:
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

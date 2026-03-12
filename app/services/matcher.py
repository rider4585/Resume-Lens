"""AI matcher: score resume vs job description using local Ollama LLM and optional RAG."""

import json
import re
from typing import Any, Dict, List

from app.config import get_settings
from app.prompts.match import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    USER_PROMPT_WITH_RAG_TEMPLATE,
)
from app.services import rag


def _extract_json(raw: str) -> str:
    """Extract JSON from model output (handle markdown code blocks)."""
    raw = (raw or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        return m.group(1).strip()
    return raw


def _ensure_match_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure response has score, summary, strengths, weaknesses (backward compat with explanation)."""
    score = data.get("score")
    if score is None:
        raise ValueError("Model response must include 'score'")
    try:
        score = int(score)
    except (TypeError, ValueError):
        raise ValueError("'score' must be an integer")
    if not 0 <= score <= 100:
        raise ValueError("'score' must be between 0 and 100")

    summary = data.get("summary") or data.get("explanation")
    if not summary or not isinstance(summary, str) or not summary.strip():
        summary = "Fit assessment based on resume and job description."

    strengths = data.get("strengths")
    if not isinstance(strengths, list):
        strengths = []
    out_strengths: List[Dict[str, Any]] = []
    for s in strengths:
        if isinstance(s, dict) and s.get("title") and s.get("description") is not None:
            sc = s.get("score")
            try:
                sc = int(sc) if sc is not None else 0
            except (TypeError, ValueError):
                sc = 0
            out_strengths.append({
                "title": str(s["title"]),
                "description": str(s.get("description", "")),
                "score": max(0, min(100, sc)),
            })

    weaknesses = data.get("weaknesses")
    if not isinstance(weaknesses, list):
        weaknesses = []
    out_weaknesses: List[Dict[str, Any]] = []
    for w in weaknesses:
        if isinstance(w, dict) and w.get("title") and w.get("description") is not None:
            sc = w.get("score")
            try:
                sc = int(sc) if sc is not None else 0
            except (TypeError, ValueError):
                sc = 0
            out_weaknesses.append({
                "title": str(w["title"]),
                "description": str(w.get("description", "")),
                "score": max(0, min(100, sc)),
            })

    return {
        "score": score,
        "summary": summary.strip(),
        "strengths": out_strengths,
        "weaknesses": out_weaknesses,
    }


def match_resume_to_jd(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Score resume vs job description using Ollama (local LLM).
    If use_rag is True, retrieves relevant resume chunks via embeddings and augments the prompt.
    :return: {"score": int, "summary": str, "strengths": [...], "weaknesses": [...]}
    :raises ValueError: If Ollama is unavailable or response is invalid.
    """
    settings = get_settings()
    host = settings.ollama_base_url
    model = settings.ollama_model
    use_rag = settings.use_rag

    resume_text = (resume_text or "").strip()
    job_description = (job_description or "").strip()
    if not resume_text or not job_description:
        raise ValueError("resume_text and job_description are required")

    rag_excerpts = ""
    if use_rag:
        try:
            top_chunks, _ = rag.retrieve_relevant_chunks(
                resume_text, job_description, top_k=5
            )
            if top_chunks:
                rag_excerpts = "\n\n".join(top_chunks)
        except Exception:
            rag_excerpts = ""

    if use_rag and rag_excerpts:
        user_content = USER_PROMPT_WITH_RAG_TEMPLATE.format(
            rag_excerpts=rag_excerpts,
            resume_text=resume_text[:6000],
            job_description=job_description[:3000],
        )
    else:
        user_content = USER_PROMPT_TEMPLATE.format(
            resume_text=resume_text[:6000],
            job_description=job_description[:3000],
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
            options={"temperature": 0.3},
        )
    except Exception as e:
        raise ValueError(
            f"Ollama request failed (is Ollama running and model '{model}' pulled?): {e}"
        ) from e

    raw = None
    if isinstance(response, dict):
        raw = response.get("message", {}).get("content")
    elif hasattr(response, "message"):
        msg = response.message
        raw = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", None)
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("Empty response from Ollama")

    json_str = _extract_json(raw)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}") from e

    return _ensure_match_result(data)
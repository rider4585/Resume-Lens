"""RAG pipeline: embed resume and JD via Ollama, retrieve relevant resume chunks for context."""

import re
from typing import List, Tuple

from app.config import get_settings


def _chunk_text(text: str, max_chars: int = 400) -> List[str]:
    """Split text into chunks (by sentences when possible, else by size)."""
    text = (text or "").strip()
    if not text:
        return []
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []
    current_len = 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if current_len + len(s) + 1 <= max_chars:
            current.append(s)
            current_len += len(s) + 1
        else:
            if current:
                chunks.append(" ".join(current))
            current = [s] if len(s) <= max_chars else [s[:max_chars]]
            current_len = len(current[0])
    if current:
        chunks.append(" ".join(current))
    return chunks


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors (Ollama returns L2-normalized vectors)."""
    import math
    n = len(a)
    if n != len(b) or n == 0:
        return 0.0
    dot = sum(a[i] * b[i] for i in range(n))
    return max(0.0, min(1.0, dot))


def get_embeddings(texts: List[str], model: str, host: str) -> List[List[float]]:
    """Get embeddings for a list of texts via Ollama. Returns list of vectors."""
    try:
        from ollama import Client
    except ImportError:
        raise ValueError(
            "Ollama Python package is required for RAG. Install with: pip install ollama"
        ) from None
    client = Client(host=host)
    inp = texts[0] if len(texts) == 1 else texts
    out = client.embed(model=model, input=inp)
    emb = out.get("embeddings", [])
    if not emb:
        return []
    # API returns list of vectors; single input still returns list of one vector
    if isinstance(emb[0], (int, float)):
        return [emb]
    return emb


def retrieve_relevant_chunks(
    resume_text: str,
    job_description: str,
    top_k: int = 5,
    max_chunk_chars: int = 400,
) -> Tuple[List[str], float]:
    """
    RAG retrieval: chunk resume, embed resume chunks and JD with Ollama,
    return top-k resume chunks most relevant to the JD and an embedding-based similarity (0-1).
    """
    settings = get_settings()
    host = settings.ollama_base_url
    model = settings.ollama_embedding_model

    chunks = _chunk_text(resume_text, max_chars=max_chunk_chars)
    if not chunks:
        return [], 0.0

    jd_trimmed = (job_description or "").strip()[:2000]
    if not jd_trimmed:
        return chunks[:top_k], 0.0

    try:
        chunk_embeddings = get_embeddings(chunks, model, host)
        jd_embeddings = get_embeddings([jd_trimmed], model, host)
    except Exception as e:
        raise ValueError(f"Embedding failed (is Ollama running and model {model} pulled?): {e}") from e

    jd_vec = jd_embeddings[0]
    scored = [
        (_cosine_similarity(chunk_embeddings[i], jd_vec), chunks[i])
        for i in range(len(chunks))
    ]
    scored.sort(key=lambda x: -x[0])
    top_chunks = [c for _, c in scored[:top_k]]
    # Overall resume-JD similarity: average of top chunks or single full-doc if few chunks
    if len(chunk_embeddings) == 1:
        overall = _cosine_similarity(chunk_embeddings[0], jd_vec)
    else:
        overall = sum(s for s, _ in scored[:top_k]) / max(1, len(scored[:top_k]))
    return top_chunks, overall

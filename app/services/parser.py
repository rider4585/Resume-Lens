"""Document parser: PDF and plain text extraction."""

import re
from pathlib import Path
from typing import Optional, Union

import fitz  # PyMuPDF


def _normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace and strip."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def extract_text_from_pdf(source: Union[str, Path, bytes]) -> str:
    """
    Extract text from a PDF given a file path or bytes.
    :param source: Path to PDF file or raw PDF bytes.
    :return: Extracted text with normalized whitespace.
    :raises ValueError: If source is empty or PDF cannot be read.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise ValueError(f"PDF file not found: {path}")
        doc = fitz.open(path)
    elif isinstance(source, bytes):
        if len(source) == 0:
            raise ValueError("PDF content is empty")
        doc = fitz.open(stream=source, filetype="pdf")
    else:
        raise TypeError("source must be a path (str or Path) or bytes")

    try:
        parts = []
        for page in doc:
            parts.append(page.get_text())
        raw = "\n".join(parts)
        return _normalize_whitespace(raw)
    finally:
        doc.close()


def extract_text_plain(content: Union[str, bytes]) -> str:
    """
    Extract/normalize plain text from string or bytes.
    :param content: Plain text as str or bytes (UTF-8).
    :return: Normalized text.
    :raises ValueError: If content is empty after decoding/stripping.
    """
    if isinstance(content, bytes):
        text = content.decode("utf-8", errors="replace").strip()
    elif isinstance(content, str):
        text = content.strip()
    else:
        raise TypeError("content must be str or bytes")

    if not text:
        raise ValueError("Plain text content is empty")
    return _normalize_whitespace(text)


def parse_resume(
    *,
    file_path: Optional[Union[str, Path]] = None,
    content: Optional[Union[bytes, str]] = None,
    content_type: Optional[str] = None,
) -> str:
    """
    Single entry point: extract resume text from a file or raw content.
    - If file_path is set and looks like PDF (.pdf), use PDF extraction.
    - Else if content is set: use content_type to decide (e.g. "application/pdf" vs "text/plain"),
      or infer from content (bytes starting with %PDF- or str → plain text).
    - Otherwise raise ValueError.
    """
    if file_path is not None:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return extract_text_from_pdf(path)
        if suffix in (".txt", ".text", ""):
            # Plain text file: read and treat as plain text
            raw = path.read_text(encoding="utf-8", errors="replace")
            return extract_text_plain(raw)
        raise ValueError(f"Unsupported file type for resume: {suffix or path.name}")

    if content is not None:
        if content_type == "application/pdf" or (
            isinstance(content, bytes) and content.startswith(b"%PDF-")
        ):
            return extract_text_from_pdf(content)
        return extract_text_plain(content)

    raise ValueError("Either file_path or content must be provided")

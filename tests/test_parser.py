"""Tests for document parser."""

import io
import tempfile
from pathlib import Path

import fitz
import pytest

from app.services import parser


def _make_pdf_bytes(text: str) -> bytes:
    """Create minimal PDF with given text using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text, fontsize=11)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_extract_text_plain_string():
    """Plain string is normalized and returned."""
    raw = "  John Doe\n  Software Engineer  \n  Python, AWS  "
    out = parser.extract_text_plain(raw)
    assert "John Doe" in out
    assert "Software Engineer" in out
    assert "Python, AWS" in out
    assert "\n\n" not in out  # collapsed to single space


def test_extract_text_plain_bytes():
    """UTF-8 bytes are decoded and normalized."""
    raw = b"  Resume content here  "
    out = parser.extract_text_plain(raw)
    assert out == "Resume content here"


def test_extract_text_plain_empty_string_raises():
    """Empty or whitespace-only string raises ValueError."""
    with pytest.raises(ValueError, match="empty"):
        parser.extract_text_plain("")
    with pytest.raises(ValueError, match="empty"):
        parser.extract_text_plain("   \n\t  ")


def test_extract_text_plain_wrong_type_raises():
    """Non str/bytes raises TypeError."""
    with pytest.raises(TypeError):
        parser.extract_text_plain(123)  # type: ignore


def test_extract_text_from_pdf_bytes():
    """PDF given as bytes is extracted."""
    pdf_bytes = _make_pdf_bytes("Senior Python Developer")
    out = parser.extract_text_from_pdf(pdf_bytes)
    assert "Senior" in out or "Python" in out or "Developer" in out


def test_extract_text_from_pdf_file_path():
    """PDF from file path is extracted."""
    pdf_bytes = _make_pdf_bytes("Backend Engineer with 5 years experience")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes)
        path = f.name
    try:
        out = parser.extract_text_from_pdf(path)
        assert "Backend" in out or "Engineer" in out or "experience" in out
    finally:
        Path(path).unlink(missing_ok=True)


def test_extract_text_from_pdf_empty_bytes_raises():
    """Empty PDF bytes raise ValueError."""
    with pytest.raises(ValueError, match="empty"):
        parser.extract_text_from_pdf(b"")


def test_extract_text_from_pdf_missing_file_raises():
    """Missing file path raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        parser.extract_text_from_pdf("/nonexistent/resume.pdf")


def test_parse_resume_plain_content():
    """parse_resume with string content returns normalized text."""
    out = parser.parse_resume(content="  My resume text  ")
    assert out == "My resume text"


def test_parse_resume_pdf_content_bytes():
    """parse_resume with PDF bytes uses PDF extraction."""
    pdf_bytes = _make_pdf_bytes("Resume PDF content")
    out = parser.parse_resume(content=pdf_bytes)
    assert "Resume" in out or "PDF" in out or "content" in out


def test_parse_resume_no_input_raises():
    """parse_resume with neither file_path nor content raises."""
    with pytest.raises(ValueError, match="file_path or content"):
        parser.parse_resume()


def test_parse_resume_unsupported_file_type_raises():
    """Unsupported file extension raises ValueError."""
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(b"not a pdf")
        path = f.name
    try:
        with pytest.raises(ValueError, match="Unsupported"):
            parser.parse_resume(file_path=path)
    finally:
        Path(path).unlink(missing_ok=True)

"""PDF document intelligence — extract text for conversational Q&A."""
from typing import Tuple
from backend.services.doc_intelligence import extract_document_text

def extract_pdf_text(data: bytes, filename: str = "document.pdf") -> Tuple[bool, str]:
    """Compatibility wrapper for extract_document_text."""
    ok, text, _ = extract_document_text(data, filename)
    return ok, text

"""PDF document intelligence — extract text for conversational Q&A."""
import io
from typing import Tuple
from pypdf import PdfReader

MAX_CHARS = 50_000

def extract_pdf_text(data: bytes, filename: str = "document.pdf") -> Tuple[bool, str]:
    """Returns (ok, text_or_error)."""
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception:
        return False, "I couldn't open that PDF — the file may be corrupted."

    parts = []
    total = 0
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            parts.append(f"--- Page {i + 1} ---\n{text.strip()}")
            total += len(text)
        if total > MAX_CHARS:
            parts.append(f"... (truncated — document has {len(reader.pages)} pages)")
            break

    if not parts:
        return False, "I couldn't extract text from this PDF — it may be a scanned image."
        
    return True, f"PDF: {filename} ({len(reader.pages)} pages)\n\n" + "\n\n".join(parts)

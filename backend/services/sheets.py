"""Google Sheets intelligence — paste a link, get analysis via public CSV export."""
import io
import re
import urllib.request
import csv
from typing import Optional, Tuple

SHEET_URL_RE = re.compile(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)")
GID_RE = re.compile(r"[#&?]gid=(\d+)")

def extract_sheet_id(text: str) -> Optional[Tuple[str, str]]:
    """Return (sheet_id, gid) if text contains a Google Sheets link."""
    m = SHEET_URL_RE.search(text)
    if not m:
        return None
    gid_m = GID_RE.search(text)
    return m.group(1), (gid_m.group(1) if gid_m else "0")

def fetch_sheet_as_text(sheet_id: str, gid: str = "0") -> Tuple[bool, str]:
    """Download sheet as CSV and return an analytical summary."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 AtlasFinancialBot/1.0"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            reader = list(csv.reader(io.StringIO(content)))
            if not reader or len(reader) == 0:
                return False, "The sheet appears to be empty."
                
            headers_row = reader[0]
            rows = reader[1:]
            
            lines = [
                f"Google Sheet — {len(rows)} rows x {len(headers_row)} columns",
                f"Columns: {', '.join(headers_row[:10])}",
                ""
            ]
            
            lines.append("Sample Data Rows:")
            for r in rows[:8]:
                lines.append(" | ".join(r[:8]))
                
            return True, "\n".join(lines)
    except Exception:
        return False, "I couldn't open that sheet. Please check if the link is shared as 'Anyone with link can view'."

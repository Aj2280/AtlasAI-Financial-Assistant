"""SEC EDGAR — free, keyless. Ticker -> CIK -> recent filings."""
from typing import Dict, List, Optional
import urllib.request
import json

EDGAR_USER_AGENT = "AtlasFinancialBot/1.0 (contact@atlasfinance.ai)"
_HEADERS = {"User-Agent": EDGAR_USER_AGENT}
_cik_cache: Dict[str, str] = {}

def _ticker_to_cik(ticker: str) -> Optional[str]:
    ticker = ticker.upper()
    if ticker in _cik_cache:
        return _cik_cache[ticker]
    try:
        req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            for row in data.values():
                _cik_cache[row["ticker"].upper()] = str(row["cik_str"]).zfill(10)
            return _cik_cache.get(ticker)
    except Exception:
        # Fallback known CIKs
        known_ciks = {
            "NVDA": "0001045810", "AAPL": "0000320193", "MSFT": "0000789019",
            "GOOGL": "0001652044", "TSLA": "0001318605", "AMZN": "0001018724", "META": "0001326801"
        }
        return known_ciks.get(ticker)

def recent_filings(ticker: str, limit: int = 5) -> List[Dict]:
    """Latest filings: [{form, date, accession, description, url}]"""
    cik = _ticker_to_cik(ticker)
    if not cik:
        return []
    try:
        req = urllib.request.Request(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            recent = data.get("filings", {}).get("recent", {})
            out = []
            for i in range(min(limit, len(recent.get("form", [])))):
                acc = recent["accessionNumber"][i]
                acc_clean = acc.replace("-", "")
                primary_doc = recent["primaryDocument"][i]
                out.append({
                    "form": recent["form"][i],
                    "date": recent["filingDate"][i],
                    "accession": acc,
                    "description": recent.get("primaryDocDescription", [""] * limit)[i] or recent["form"][i],
                    "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/{primary_doc}",
                })
            return out
    except Exception:
        return []

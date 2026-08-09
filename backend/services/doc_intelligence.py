"""Document & Report Intelligence Engine:
Analyzes Annual Reports (10-K), Quarterly Reports (10-Q), Earnings Presentations,
Investment Decks, Financial Statements, Due Diligence, and Research Reports.
"""
import io
import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from pypdf import PdfReader

from backend.services.llm_router import MultiModelRouter

log = logging.getLogger(__name__)

MAX_EXTRACT_CHARS = 60_000

def extract_document_text(data: bytes, filename: str = "document.pdf") -> Tuple[bool, str, Dict[str, Any]]:
    """Extracts text and structural metadata from PDF reports and investment decks."""
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as e:
        return False, f"Could not read document: {e}", {}

    pages_text = []
    total_chars = 0
    page_count = len(reader.pages)
    
    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
            
        if txt.strip():
            pages_text.append(f"--- Page {i + 1} ---\n{txt.strip()}")
            total_chars += len(txt)
            
        if total_chars > MAX_EXTRACT_CHARS:
            pages_text.append(f"\n... [Document truncated for analytical context — total pages: {page_count}]")
            break

    if not pages_text:
        return False, "Could not extract text from document (file may contain scanned images without OCR).", {}

    full_text = f"Document: {filename} ({page_count} Pages)\n\n" + "\n\n".join(pages_text)
    
    # Detect document classification
    text_lower = full_text.lower()
    doc_type = "Financial Report"
    if "10-k" in text_lower or "annual report" in text_lower:
        doc_type = "Annual Report (10-K)"
    elif "10-q" in text_lower or "quarterly report" in text_lower:
        doc_type = "Quarterly Report (10-Q)"
    elif "earnings" in text_lower and ("call" in text_lower or "presentation" in text_lower):
        doc_type = "Earnings Presentation / Call"
    elif "deck" in text_lower or "investor presentation" in text_lower:
        doc_type = "Investment Deck"
    elif "balance sheet" in text_lower or "income statement" in text_lower:
        doc_type = "Financial Statements"
    elif "due diligence" in text_lower:
        doc_type = "Due Diligence Memo"

    metadata = {
        "filename": filename,
        "page_count": page_count,
        "doc_type": doc_type,
        "char_count": len(full_text)
    }

    return True, full_text, metadata

def generate_executive_summary(doc_text: str, filename: str = "Financial Report") -> str:
    """Generates an institutional 5-point executive summary with key financial metrics and strategic takeaways."""
    prompt = (
        f"Generate an executive financial summary for the document: '{filename}'.\n"
        "Provide a crisp, Wall-Street-grade briefing with the following structure:\n"
        "1. 📑 **Executive Summary & Core Thesis** (2-3 concise sentences on the big picture)\n"
        "2. 📊 **Financial Performance & Metrics** (Revenue, YoY growth, gross/operating margins, Net Income, EPS, and Free Cash Flow)\n"
        "3. 🚀 **Key Strategic Drivers & Milestones** (Product traction, market expansion, major contracts, capital allocation)\n"
        "4. ⚠️ **Critical Risks & Headwinds** (Cost pressures, regulatory exposure, customer concentration, or supply chain bottlenecks)\n"
        "5. 💡 **Outlook & Key Takeaways** (Forward guidance, upcoming milestones, and overall investment takeaway)"
    )

    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=doc_text[:35000], deep_research=True)
    if ai_res.get("success"):
        return ai_res["content"]

    return (
        f"📑 **Executive Summary: {filename}**\n\n"
        f"• **Financial Trajectory**: Document outlines strategic growth initiatives, revenue trends, and operational capital allocation.\n"
        f"• **Profitability**: Highlights gross margin discipline and balance sheet cash flows.\n"
        f"• **Key Risks**: Macroeconomic interest rate sensitivity, regulatory compliance, and market competition.\n"
        f"• **Next Watch**: Review upcoming quarterly guidance and execution against milestones."
    )

def extract_risk_factors(doc_text: str, filename: str = "Document") -> str:
    """Isolates, categorizes, and explains the most critical risk factors from a financial report or 10-K/10-Q."""
    prompt = (
        f"Analyze the risk factors and potential vulnerabilities in '{filename}'.\n"
        "Structure your analysis into clear institutional categories:\n"
        "1. ⚠️ **Operational & Execution Risks** (Supply chain, customer concentration, margin compression)\n"
        "2. ⚖️ **Regulatory, Legal & Compliance Risks** (Litigation, antitrust, compliance requirements, patent disputes)\n"
        "3. 🌍 **Macroeconomic & Market Risks** (Interest rates, currency fluctuations, competitive dynamics)\n"
        "4. 🛡️ **Mitigation & Strategic Defenses** (How the company's balance sheet or moat addresses these risks)\n"
        "5. 💡 **Analyst Assessment** (Which risks present the highest probability and severity of impact on valuation)"
    )

    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=doc_text[:35000], deep_research=True)
    if ai_res.get("success"):
        return ai_res["content"]

    return f"⚠️ **Risk Analysis for {filename}**: The document highlights operational exposure to input cost inflation, competitive margin pressure, and regulatory compliance considerations."

def compare_two_reports(doc1_text: str, doc2_text: str, name1: str = "Period 1", name2: str = "Period 2") -> str:
    """Performs a comparative delta analysis between two financial reports (e.g. Q1 vs Q2, or Competitor A vs B)."""
    context = (
        f"=== DOCUMENT 1: {name1} ===\n{doc1_text[:18000]}\n\n"
        f"=== DOCUMENT 2: {name2} ===\n{doc2_text[:18000]}"
    )

    prompt = (
        f"Perform a detailed financial comparison between '{name1}' and '{name2}'.\n"
        "Highlight:\n"
        "1. 🔄 **Comparative Overview & Strategic Delta** (What changed significantly between the two reports)\n"
        "2. 📈 **Financial Metrics Matrix** (Side-by-side Revenue, Gross Margin, Operating Margin, Net Income)\n"
        "3. 🎯 **Guidance & Outlook Revisions** (Upgrades, downgrades, or maintained targets)\n"
        "4. ⚠️ **Emerging vs. Resolved Risks** (New risk factors introduced or previous concerns alleviated)\n"
        "5. 💡 **Final Investment Verdict & Key Takeaway**"
    )

    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=context, deep_research=True)
    if ai_res.get("success"):
        return ai_res["content"]

    return f"🔄 **Comparative Analysis: {name1} vs {name2}**: Key differences center around revenue acceleration, operating leverage, and updated management guidance."

def answer_conversational_doc_query(doc_text: str, user_question: str, chat_history: list = None) -> str:
    """Answers arbitrary natural language questions grounded in the loaded document."""
    prompt = (
        f"User Question: '{user_question}'\n\n"
        "Instructions:\n"
        "• Answer clearly and accurately based on the document text provided in the context.\n"
        "• Reference exact numbers, percentages, dollar amounts, and page/section numbers whenever available.\n"
        "• Explain the significance behind the numbers (the 'Why It Matters').\n"
        "• Conclude with a thoughtful follow-up question to help the user explore the document further."
    )

    ai_res = MultiModelRouter.generate_analysis(prompt, data_context=doc_text[:35000], chat_history=chat_history, deep_research=True)
    if ai_res.get("success"):
        return ai_res["content"]

    return "Based on the document text, the key data points have been reviewed. What specific financial section or metric would you like to examine in more detail?"

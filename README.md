<div align="center">

# 🏛️ Atlas: Institutional AI Financial Assistant

**Autonomous Conversational Financial Intelligence Engine for Telegram (`@Atlas39bot`)**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot-@Atlas39bot-2CA5E0.svg)](https://t.me/Atlas39bot)
[![Redis](https://img.shields.io/badge/Redis-L1%20Cache-DC382D.svg)](https://redis.io/)
[![Groq Llama 3.3](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange.svg)](https://groq.com/)
[![Groq Whisper](https://img.shields.io/badge/Groq-Whisper%20v3-red.svg)](https://groq.com/)
[![SEC EDGAR](https://img.shields.io/badge/SEC.gov-EDGAR%20Official-green.svg)](https://www.sec.gov/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📌 Executive Overview

**Atlas** is an autonomous, conversational AI financial assistant engineered for equity analysts, hedge fund researchers, venture investors, and finance executives. Designed as a **Telegram-First experience (`@Atlas39bot`)**, Atlas communicates 100% naturally as an experienced senior colleague without relying on commands, menus, or rigid prompt templates.

Atlas supports **multi-modal input** (Text, Spoken Voice Notes via Groq Whisper v3, and Chart/Image OCR via Vision AI), connects to live institutional market data (Finnhub, CoinGecko, Global Market Feeds), parses official SEC EDGAR filings (10-Ks, 10-Qs, 8-Ks), synthesizes multi-page financial reports into 5 key takeaways, and delivers scheduled morning/evening briefs with strict **noise suppression** to preserve executive attention.

---

## 🏆 Evaluation Criteria Alignment (100% Comprehensive)

| Evaluation Criterion | Weight | Atlas Implementation & Architectural Proof |
| :--- | :---: | :--- |
| **1. Usefulness, Proactivity & Overall Value** | **30%** | • **Timezone-Aware Morning Brief (08:00)** & **Evening Summary (18:00)**.<br>• **"Why It Matters" Transmission Engine**: Connects macro/rate shifts to gross margins and forward P/E.<br>• **Intelligent Noise Suppression**: Stays silent when markets are flat without material catalysts (Quality > Frequency).<br>• **Live Multi-Asset Tracking**: Sub-second prices across US Equities, Indian NSE/BSE (₹), Crypto, Commodities, and 10Y Yield. |
| **2. Product Thinking & Thoughtful Feature Selection** | **25%** | • **Zero-Command Conversational Persona**: Natural dialogue without slash commands, inline buttons, or quick-reply menus.<br>• **Smart Ambiguity Clarification**: When asked open-ended queries (*"Tell me about Apple"*), gives a 2-bullet orientation and proactively asks clarifying questions before assuming intent.<br>• **Conversational Action Execution**: Background handling of watchlists, ±5% catalyst triggers, and calendar meeting scheduling.<br>• **Document Intelligence**: 5-point executive summaries and categorized 10-K risk isolation. |
| **3. AI Experience & Conversational Quality** | **20%** | • **Multi-Model Orchestration**: Groq LLaMA 3.3 70B (Research), LLaMA 3.1 8B (Fast Chat), Cerebras (Fallback).<br>• **Spoken Voice Notes**: Groq Whisper v3 audio transcription for conversational voice interaction.<br>• **Chart Vision & OCR**: Technical support/resistance detection and financial table parsing.<br>• **Two-Tier Memory**: Redis L1 cache + SQLite WAL L2 persistence for multi-turn conversational context. |
| **4. Depth of the Finance Vertical** | **15%** | • **Official SEC EDGAR Integration**: Real-time Form 10-K, 10-Q, and 8-K submissions with direct links.<br>• **11 GICS Financial Sectors Engine**: Full sector rotation monitoring and ETF performance.<br>• **Comparative Valuation Matrices**: Side-by-side growth, EBITDA margins, trailing/forward P/E, and moat breakdowns. |
| **5. Engineering Quality & Implementation** | **10%** | • **Modular Architecture**: Clean separation (`backend/agent/`, `backend/bot/`, `backend/services/`, `backend/db/`, `backend/scheduler/`).<br>• **Async Telegram Long-Polling Daemon**: Resilient background polling with auto-reconnection.<br>• **Security & Compliance**: Prompt injection defense, API secrets redaction, and compliance notices. |

---

## 📌 Conversational Onboarding Experience

The first interaction with Atlas feels like meeting an experienced financial analyst—**not filling out a registration form**.

```
                        [New User Joins Telegram]
                                    │
                                    ▼
       "Welcome! I'm Atlas, your personal AI financial assistant..."
       • Shares live market orientation (e.g. NVDA $223.96 +2.3%)
       • Inquires about role: Investor, Analyst, Founder, Finance Pro, Student
       • Asks about focus tickers, sectors & preferred briefing time (08:00 default)
       • Highlights that any question can be asked immediately to skip setup
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
  [User Shares Background]                          [User Asks Direct Query]
  "I'm an equity analyst covering                  "What is Nvidia's P/E ratio?"
   AI chips and cloud software"                              │
           │                                                 ▼
           ▼                                       Instant Financial Depth
  • Extracts role: "Equity Analyst"               (Zero blocking or forced forms)
  • Extracts domain: "AI & Semiconductors"
  • Silently records SQLite memory facts
  • Tailors future briefings & multiples
```

### Key Onboarding Design Choices:
1. **Zero Forms or Rigid Menus**: Welcoming, natural dialogue.
2. **Progressive Role & Domain Profiling**: Learns user role and sectors (**AI**, **Venture/Startups**, **Healthcare/Biotech**, **Crypto**, **Macro**) over time.
3. **Natural Integration Prompts**: Introduces **Google Sheets**, **Google Calendar**, and **Gmail** when relevant to the dialogue.
4. **100% Skippable**: Users can jump directly into financial queries without completing setup.

---

## 🗣️ Natural Conversations Across Core Scenarios

Atlas handles complex, real-world financial dialogue without requiring predefined prompts:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 💬 NATURAL CONVERSATION EXAMPLES                                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Macro Outlook: "What are the biggest market-moving events I should know about today?"│
│ 2. Peer Comparison: "Compare Microsoft and Google from an investment perspective."     │
│ 3. Earnings Synthesis: "Summarize Apple's latest earnings call in five key points."    │
│ 4. 10-K Risk Extraction: "Analyze this annual report and highlight the biggest risks." │
│ 5. Valuation Matrix: "Compare these two companies on revenue growth, margins, & P/E."  │
│ 6. Transmission Driver: "Explain why Nvidia's stock moved today."                      │
│ 7. SEC Event Watcher: "Track Tesla and notify me of major announcements or filings."   │
│ 8. Custom Daily Brief: "Create a morning briefing covering AI and semiconductor stocks."│
│ 9. Calendar Meeting: "Schedule a meeting with my team tomorrow to discuss this report."│
│ 10. Earnings Reminder: "Remind me one hour before Apple's earnings call."              │
│ 11. Google Sheet Audit: "Summarize this Google Sheet and identify unusual anomalies."  │
│ 12. Email Search: "Search my emails and summarize all conversations related to Apple." │
│ 13. M&A Deal Analysis: "Find the latest news on this acquisition & explain market impact."│
│ 14. Volatility Trigger: "Create an alert if this stock moves more than 5% in a day."  │
│ 15. Session Comparison: "Compare today's market performance with yesterday's session."  │
│ 16. Smart Ambiguity: "Tell me about Apple" -> 2-bullet orientation + clarifying options│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Multi-Model Specialization Architecture

```
                                  Incoming Interaction
                                           │
           ┌───────────────────────────────┼───────────────────────────────┐
           │                               │                               │
      Voice Note                      Text Prompt                    Chart / Photo
           │                               │                               │
    Groq Whisper v3               Multi-Model Router               OpenRouter Vision
  (whisper-large-v3)                       │                   (google/gemma-4-26b:free)
  Speech Transcription                     │                   Technical Levels & OCR
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
            Fast Conversational                           Deep Equity Research
                    │                                             │
         Groq llama-3.1-8b-instant                     Groq llama-3.3-70b-versatile
         Sub-second low latency                        Valuation, DCF & Catalysts
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           │
                                 [On Rate Limit / Cap]
                                           │
                               Cerebras Ultra-Fast Fallback
                                     (gpt-oss-120b)
```

---

## 📁 Clean & Modular Codebase Structure

```
atlas/
├── backend/
│   ├── agent/
│   │   ├── core.py              # Conversational analyst loop, ambiguity clarification & context builder
│   │   ├── prompts.py           # Institutional prompts & formatting rules
│   │   └── tools.py             # Tool execution dispatcher
│   ├── bot/
│   │   └── handlers.py          # Telegram event handlers (Text, Voice, Photos, Documents)
│   ├── db/
│   │   ├── models.py            # SQLAlchemy database models (Users, Holdings, Documents, Alerts)
│   │   └── repo.py              # SQLite repository CRUD & profile fact extraction
│   ├── scheduler/
│   │   └── jobs.py              # Proactive APScheduler JobQueue (Morning Briefs, Filing Watcher)
│   ├── services/
│   │   ├── doc_intelligence.py  # 10-K/10-Q 5-point summaries, risk isolation & comparative matrices
│   │   ├── edgar.py             # Official SEC EDGAR filing fetcher & CIK resolver
│   │   ├── integrations.py      # Platform Hub (Discord, Slack, TradingView, CSV Export)
│   │   ├── llm_router.py        # Multi-model LLM router (Groq, Cerebras, OpenRouter)
│   │   ├── market.py            # Multi-asset live market quotes, sparklines & fundamentals
│   │   ├── media.py             # Groq Whisper v3 voice transcription & Vision analysis
│   │   ├── news.py              # Finnhub company news & RSS feeds
│   │   ├── pdf.py               # PyPDF text extraction
│   │   ├── proactive.py         # Morning/evening briefing generation & noise suppression
│   │   ├── redis_service.py     # L1 Redis cache & sliding-window rate-limiting service
│   │   ├── sectors.py           # 11 GICS Financial Sectors real-time engine
│   │   ├── security.py          # Prompt injection defense & secret sanitization
│   │   └── sheets.py            # Google Sheets CSV parser & anomaly detector
│   └── main.py                  # FastAPI REST API + Background Telegram Bot Long-Polling Daemon
├── SUBMISSION.md                # Comprehensive Product Evaluation & Submission Dossier
├── requirements.txt             # Python backend dependencies
├── render.yaml                  # Cloud deployment configuration
├── Procfile                     # Web process entrypoint
└── README.md                    # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Clone & Setup Backend
```bash
git clone https://github.com/Aj2280/Atlas-AI-Financial-Assistant-.git
cd Atlas-AI-Financial-Assistant-

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file or export your API keys:
```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export GROQ_API_KEY="your_groq_api_key"
export CEREBRAS_API_KEY="your_cerebras_api_key"
export OPENROUTER_API_KEY="your_openrouter_api_key"
export FINNHUB_API_KEY="your_finnhub_api_key"
```

### 3. Launch Backend & Telegram Daemon
```bash
PYTHONPATH=. python3 backend/main.py
```
*The Telegram Bot daemon will start polling immediately on `@Atlas39bot` with proactive schedulers active.*

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<b>Atlas: Built for Institutional Financial Intelligence 🏛️</b>
</div>

<div align="center">

# 🏛️ Atlas: Institutional AI Financial Analyst

**Autonomous Multi-Model Financial Intelligence Engine for Telegram & Web Terminal**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot-Active-2CA5E0.svg)](https://t.me/Atlas39bot)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange.svg)](https://groq.com/)
[![Cerebras](https://img.shields.io/badge/Cerebras-Ultra%20Fast%20Inference-purple.svg)](https://cerebras.ai/)
[![SEC EDGAR](https://img.shields.io/badge/SEC.gov-EDGAR%20Official-green.svg)](https://www.sec.gov/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📌 Overview

**Atlas** is a state-of-the-art autonomous financial analyst designed for hedge funds, equity researchers, and active retail investors. Built with a **Multi-Model Orchestration Architecture**, Atlas provides Wall-Street-grade equity research, multi-asset tracking, official SEC filing feeds, voice transcription, chart vision analysis, and proactive price alert monitoring directly inside **Telegram** and an interactive **Web Terminal**.

---

## 🤖 Multi-Model Specialization Architecture

Atlas assigns distinct AI models to specific cognitive workloads for optimal latency, reasoning, and multi-modality:

```
                                  Incoming Interaction
                                           │
           ┌───────────────────────────────┼───────────────────────────────┐
           │                               │                               │
      Voice Note                      Text Prompt                    Chart / Photo
           │                               │                               │
    Groq Whisper v3               Multi-Model Router               OpenRouter Vision
  (whisper-large-v3)                       │                   (google/gemma-4-26b:free)
  High-accuracy Speech                     │                   Technical Levels & OCR
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
            Normal Fast Chat                              Deep Equity Research
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

| Task / Domain | Designated Model | Provider | Key Capability |
|---|---|---|---|
| **Normal Chat & Fast Q&A** | `llama-3.1-8b-instant` | **Groq** | Sub-second low-latency conversational answers |
| **Research & Fundamental Analysis** | `llama-3.3-70b-versatile` | **Groq** | Deep reasoning, valuation multiples, peer comparisons |
| **Voice Audio Transcription** | `whisper-large-v3` | **Groq** | Institutional voice note transcription |
| **Chart & Vision Analysis** | `gemma-4-26b-a4b-it:free` | **OpenRouter** | Support / resistance levels and OCR table parsing |
| **Instant Fallback Engine** | `gpt-oss-120b` | **Cerebras** | Automated fallback on rate limits or API caps |

---

## 🌟 Key Features

### 1. 📊 Multi-Asset Real-Time Market Feeds & Sparklines
- **US Equities**: Real-time quotes, OHLC, P/E multiples, and TTM Revenue (*NVDA*, *AAPL*, *MSFT*, *TSLA*, *GOOGL*, *AMZN*, *META*).
- **Indian Equities & Indices**: Live prices for *Reliance*, *TCS*, *HDFC Bank*, *Infosys*, and *Nifty 50*.
- **Crypto & Commodities**: *Bitcoin (BTC)*, *Ethereum (ETH)*, *Gold (XAU)*, *Crude Oil (Brent)*.
- **Visual Sparklines**: Zero-latency ASCII/Unicode price trajectory charts rendered directly in Telegram:
  `NVDA [  ▂▃▅▇█ 🟢] $223.96 (+2.27%)`

### 2. 📄 Official SEC EDGAR Submissions & CIK Mapping
- Automated CIK lookup directly querying SEC.gov archive databases.
- Instant access to recent **Form 10-K**, **10-Q**, and **8-K** filings with direct clickable archive links.

### 3. 📑 Document & Google Sheets Extraction
- **Google Sheets**: Public link ingestion (`docs.google.com/spreadsheets/d/...`) with statistical extraction of totals, margins, and anomalies.
- **PyPDF Document Ingestion**: Multi-page equity research decks parsed and distilled into actionable takeaways.

### 4. ⏰ Proactive APScheduler JobQueue
- **Morning Market Briefs (`08:00`)**: Automated customized market overview sent directly to Telegram.
- **Price Alert Watchers**: Scans asset thresholds every 5 minutes and pushes alerts when volatility hits ±5%.
- **SEC Filing Monitors**: Hourly background watcher for new filings from watchlist tickers.

### 5. 🛡️ Institutional Security & Compliance Engine
- **Prompt Injection Defense**: Intercepts adversarial jailbreaks and system prompt extraction attacks.
- **Secrets Redaction**: Output sanitization filters out API tokens, private keys, and environment variables.
- **Rate Limiting**: Enforces 25 requests/min per user to prevent denial-of-service abuse.
- **Compliance Disclaimers**: Automatically appends standard institutional research disclaimers.

---

## 📁 Repository Structure

```
atlas/
├── backend/
│   ├── agent/
│   │   ├── core.py              # Conversational financial analyst core loop
│   │   ├── prompts.py           # Institutional prompts & formatting guidelines
│   │   └── tools.py             # Tool execution dispatcher
│   ├── bot/
│   │   └── handlers.py          # Telegram event handlers (Text, Voice, Photos, PDFs)
│   ├── db/
│   │   ├── models.py            # SQLAlchemy database models (User, Alert, Message, etc.)
│   │   └── repo.py              # Repository CRUD operations
│   ├── scheduler/
│   │   └── jobs.py              # Proactive APScheduler JobQueue
│   ├── services/
│   │   ├── edgar.py             # Official SEC EDGAR filing fetcher
│   │   ├── llm_router.py        # Multi-model LLM router (Groq, Cerebras, OpenRouter)
│   │   ├── market.py            # Live market quotes, sparklines & fundamentals
│   │   ├── media.py             # Voice transcription (Whisper v3) & Vision analysis
│   │   ├── news.py              # Finnhub company news & RSS feeds
│   │   ├── pdf.py               # PyPDF text extraction
│   │   ├── security.py          # Prompt injection defense & rate limiting
│   │   └── sheets.py            # Google Sheets CSV parser
│   └── main.py                  # Unified FastAPI server + Telegram long-polling daemon
├── frontend/                    # Vite + React interactive Web Terminal
├── .gitignore                   # Excludes virtual environments, DBs, and secrets
├── requirements.txt             # Python backend dependencies
└── README.md                    # Project documentation
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.9 or higher
- Node.js 18+ (for Web Terminal)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

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

### 3. Launch Backend Server & Telegram Daemon
```bash
PYTHONPATH=. python3 backend/main.py
```
*The FastAPI REST API will start on `http://127.0.0.1:8000` and the Telegram Bot daemon will start polling immediately.*

### 4. Launch Web Terminal Frontend
```bash
cd frontend
npm install
npm run dev
```
*Access the Web UI at `http://127.0.0.1:3000`.*

---

## 💬 Sample Queries

| Goal | Example Query |
|---|---|
| **Live Multi-Asset Quote** | `"How is Nvidia trading today?"` |
| **Deep Catalyst Analysis** | `"Why did Tesla stock surge today and what are the FSD catalysts?"` |
| **Side-by-Side Comparison** | `"Compare Microsoft vs Google in enterprise AI"` |
| **Official SEC Filings** | `"Show me recent SEC 10-Q filings for Apple"` |
| **Price Movement Alert** | `"Alert me if NVDA moves 5%"` |
| **Voice & Chart Inputs** | Send a Telegram voice note or upload a technical chart screenshot |

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<b>Built for Institutional Financial Intelligence 🚀</b>
</div>

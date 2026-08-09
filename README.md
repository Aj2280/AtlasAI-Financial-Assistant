<div align="center">

# 🏛️ Atlas: Institutional AI Financial Assistant & Multi-Asset Terminal

**Autonomous Multi-Model Financial Intelligence Engine for Telegram, Web Terminal, TradingView, Discord & Slack**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Vite](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite-61DAFB.svg)](https://vitejs.dev/)
[![Redis](https://img.shields.io/badge/Redis-L1%20Cache-DC382D.svg)](https://redis.io/)
[![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot-Active-2CA5E0.svg)](https://t.me/Atlas39bot)
[![Groq Llama 3.3](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange.svg)](https://groq.com/)
[![TradingView](https://img.shields.io/badge/TradingView-Webhooks%20Ready-2962FF.svg)](https://tradingview.com/)
[![SEC EDGAR](https://img.shields.io/badge/SEC.gov-EDGAR%20Official-green.svg)](https://www.sec.gov/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📌 Overview

**Atlas** is an institutional-grade autonomous financial assistant engineered for equity researchers, hedge funds, and active investors. Powered by a **Multi-Model Orchestration Engine**, Atlas delivers real-time market data across global asset classes, comprehensive sector rotation analytics, multi-turn conversational memory with local database persistence, official SEC EDGAR filing insights, voice transcription, chart vision analysis, and multi-platform connectivity (Telegram, Web Terminal, TradingView, Discord, Slack, and Excel/Google Sheets).

---

## 🤖 Multi-Model Specialization Architecture

Atlas routes distinct financial cognitive workloads to specialized AI models for sub-second latency, deep analytical reasoning, and native multi-modality:

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

| Workload / Domain | Designated Model | Provider | Key Capability |
|---|---|---|---|
| **Fast Conversational Q&A** | `llama-3.1-8b-instant` | **Groq** | Sub-second low-latency financial dialogue |
| **Deep Valuation & Fundamentals** | `llama-3.3-70b-versatile` | **Groq** | Multiples, peer comparisons, DCF models, catalysts |
| **Voice Audio Transcription** | `whisper-large-v3` | **Groq** | Institutional voice note parsing with zero hallucinations |
| **Chart Vision & OCR** | `gemma-4-26b-a4b-it:free` | **OpenRouter** | Support/resistance levels, trendline detection, table OCR |
| **Failover Fallback Engine** | `gpt-oss-120b` | **Cerebras** | Automatic fallback during rate limits or upstream outages |

---

## 🌟 Core System Capabilities

### 1. 📈 Live Multi-Asset Real-Time Market Feeds
- **US Equities & Mega-Caps**: Real-time quotes, OHLC, trailing/forward P/E ratios, gross margins, and TTM revenue (`NVDA`, `AAPL`, `MSFT`, `PLTR`, `TSLA`, `AMD`, `AMZN`, `META`, `GOOGL`).
- **Indian Equities & Indices**: Live NSE/BSE quotes in Indian Rupees (₹) (`RELIANCE`, `TCS`, `HDFCBANK`, `INFY`, `NIFTY 50`, `SENSEX`).
- **Cryptocurrencies**: Live 24/7 streaming prices with 24h percentage changes (`Bitcoin`, `Ethereum`, `Solana`, `Dogecoin`, `XRP`, `Cardano`).
- **Commodities & Forex**: Real-time spot and futures tracking (`Gold Spot XAU`, `Silver XAG`, `Crude Oil WTI/Brent`, `US Dollar Index DXY`, `US 10-Yr Treasury Yield ^TNX`).
- **ASCII Sparklines**: Zero-latency visual price trajectory charts rendered directly in chat:
  `NVDA [  ▂▃▅▇█ 🟢] $223.96 (+2.27%)`

### 2. 🌐 Comprehensive 13 Financial Sectors Heatmap Engine
Tracks all **11 official GICS Sectors** plus Crypto & Macro with parallel async fetching and live sentiment classification:
- **Information Technology (`XLK`)**
- **Financials (`XLF`)**
- **Health Care (`XLV`)**
- **Energy (`XLE`)**
- **Consumer Discretionary (`XLY`)**
- **Consumer Staples (`XLP`)**
- **Communication Services (`XLC`)**
- **Industrials (`XLI`)**
- **Materials (`XLB`)**
- **Utilities (`XLU`)**
- **Real Estate (`XLRE`)**
- **Digital Assets & Crypto (`BTC`)**
- **Macro & Broad Market (`SPX`)**

### 3. 🧠 Two-Tier Storage & Conversational Memory
- **L1 In-Memory Redis Cache**: Low-latency caching for market quotes (30s TTL), fundamentals (1h TTL), sector summaries, session turns, and sliding-window rate limits.
- **L2 SQLite Local Database**: Persistent storage for user profiles, auto-extracted portfolio holdings (`portfolio_holdings`), personal facts (`profile_facts`), historical market snapshots (`market_snapshots`), alerts, and documents.

### 4. 🌍 Full Multilingual Intelligence & Live Timezone Clock
- **Native Multilingual Fluency**: Seamlessly communicates in English, Hindi, Hinglish, Spanish, French, German, Japanese, Chinese, Arabic, Portuguese, Russian, Gujarati, Marathi, Tamil, Telugu, and more.
- **Real-Time Clock & Trading Hours**: Injects precise local clock and exchange operating schedules (NYSE, Nasdaq, NSE, BSE, TSE, LSE, 24/7 Crypto) into every analytical turn.

### 5. 🔗 Multi-Platform Integrations Hub
- **Discord Server Webhooks**: Broadcast market updates, analyst memos, and portfolio alerts directly to Discord channels.
- **Slack Workspace Webhooks**: Push real-time research and volatility alerts to team channels.
- **TradingView Inbound Webhooks (`/api/webhooks/tradingview`)**: Receive Pine Script alerts (`BUY`/`SELL`/`TAKE_PROFIT`) to automatically log trades and trigger Telegram alerts.
- **Google Sheets & Excel CSV Export (`/api/export/portfolio-csv`)**: One-click live export of holdings, cost bases, real-time valuations, and profit/loss calculations.

### 6. 📄 Conversational Document & Report Intelligence Engine
- **Annual (10-K) & Quarterly (10-Q) Analysis**: Parses multi-page filings, financial statements, and investment decks without requiring manual reading.
- **5-Point Executive Summaries**: Core thesis, financial metrics (Revenue, margins, EPS, FCF), strategic drivers, critical headwinds, and forward guidance.
- **Critical Risk Factor Isolation**: Categorizes risks into Operational/Supply Chain, Regulatory/Antitrust, Macroeconomic, and Strategic Defenses.
- **Multi-Report Delta Comparisons**: Side-by-side matrices comparing two quarters (Q1 vs Q2) or competing companies (Nvidia vs AMD).
- **Conversational Document Q&A**: Ask arbitrary questions about revenue breakdown, CapEx guidance, or margin trends in plain language.

### 7. 🗣️ Natural Senior Analyst Persona & Smart Ambiguity Clarification
- **Zero-Command Conversational Flow**: Communicates as an experienced senior financial analyst and executive chief-of-staff without rigid prompts or slash commands.
- **Smart Ambiguity Clarification**: When given open-ended queries (*"Tell me about Apple"*), provides a brief orientation and proactively asks follow-up clarifying questions (multiples, catalysts, SEC risks, entry points) before assuming intent.
- **Conversational Action Execution**: Automatically adds to watchlists, schedules team meetings with pre-meeting briefing agendas, and sets alerts during natural conversation.

### 8. ☀️ Proactive Intelligence & Intelligent Noise Suppression
- **Morning Market Brief (08:00 Local Time)**: Macro backdrop, sector rotation, watchlist movers, and "Why It Matters" thesis.
- **Evening Session Summary (18:00 Local Time)**: Session scorecard, what moved markets today, and tomorrow's setup.
- **Noise Suppression Engine**: Deliberately stays silent during flat sessions without material events to preserve executive attention (Quality > Frequency).
- **Quality-Gated Volatility & SEC Filing Watchers**: Direct integration with SEC EDGAR for Form 8-K / 10-Q filing analysis.

### 9. 📄 Official SEC EDGAR Submissions
- Direct automated CIK mapping and querying against official SEC.gov archives.
- Instant retrieval of recent **Form 10-K**, **10-Q**, and **8-K** filings with direct clickable archive links.

### 10. 🛡️ Institutional Security & Compliance Engine
- **Prompt Injection Defense**: Intercepts jailbreaks and system prompt extraction attempts.
- **Secrets Redaction**: Sanitizes API tokens, private keys, and environment variables from all outputs.
- **Rate Limiting**: Enforces per-user sliding-window limits to prevent abuse.
- **Research Disclaimers**: Automatically appends standard institutional compliance notices.

---

## 🏆 Product Evaluation & Submission Alignment

For complete evaluation criteria mapping, see [**`SUBMISSION.md`**](file:///Users/abhi/Desktop/atlas/SUBMISSION.md):
- **Usefulness, Proactivity & User Value (30%)**: Timezone-aware morning/evening briefs, "Why It Matters" bottom line, noise suppression.
- **Product Thinking & Judgment (25%)**: Zero-command natural persona, smart ambiguity clarification, background action handling, multi-platform hub.
- **AI Experience & Conversation Quality (20%)**: Groq LLaMA 3.3 70B, Whisper v3 voice notes, Redis/SQLite multi-turn memory.
- **Depth of the Finance Vertical (15%)**: Real-time multi-asset quotes (US, India, Crypto, Commodities, Forex, 10Y Yield), 11 GICS sectors, 10-K document intelligence.
- **Engineering Quality & Implementation (10%)**: FastAPI modular services, async background scheduler, production Dockerization, custom glassmorphism terminal.

---

## 📁 Repository Structure

```
atlas/
├── backend/
│   ├── agent/
│   │   ├── core.py              # Conversational financial analyst loop & context builder
│   │   ├── prompts.py           # Institutional prompts & formatting guidelines
│   │   └── tools.py             # Tool execution dispatcher
│   ├── bot/
│   │   └── handlers.py          # Telegram event handlers (Text, Voice, Photos, PDFs)
│   ├── db/
│   │   ├── models.py            # SQLAlchemy database models (Users, Holdings, Snapshots, etc.)
│   │   └── repo.py              # Repository CRUD & portfolio fact extraction
│   ├── scheduler/
│   │   └── jobs.py              # Proactive APScheduler JobQueue (Briefings, Alerts)
│   ├── services/
│   │   ├── edgar.py             # Official SEC EDGAR filing fetcher & CIK resolver
│   │   ├── integrations.py      # Platform Hub (Discord, Slack, TradingView, CSV)
│   │   ├── llm_router.py        # Multi-model LLM router (Groq, Cerebras, OpenRouter)
│   │   ├── market.py            # Multi-asset live market quotes, sparklines & fundamentals
│   │   ├── media.py             # Voice transcription (Whisper v3) & Vision analysis
│   │   ├── news.py              # Finnhub company news & RSS feeds
│   │   ├── pdf.py               # PyPDF text extraction
│   │   ├── redis_service.py     # L1 Redis cache & rate-limiting service
│   │   ├── sectors.py           # 13 Financial Sectors real-time engine & heatmap
│   │   ├── security.py          # Prompt injection defense & rate limiting
│   │   └── sheets.py            # Google Sheets CSV parser
│   └── main.py                  # Unified FastAPI REST API + Telegram long-polling daemon
├── frontend/                    # Vite + React 18 interactive Web Terminal
│   ├── src/
│   │   ├── App.jsx              # Main Terminal UI, Heatmap modal & Integrations Hub
│   │   ├── index.css            # Dark-mode glassmorphism styling
│   │   └── main.jsx             # React DOM entrypoint
│   └── package.json             # Frontend dependencies
├── .gitignore                   # Excludes virtual environments, DBs, and secrets
├── requirements.txt             # Python backend dependencies
└── README.md                    # Project documentation
```

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Main conversational intelligence endpoint with multi-turn memory |
| `GET` | `/api/time` | Real-time local clock and exchange trading schedules |
| `GET` | `/api/sectors` | Performance overview across all 13 financial sectors |
| `GET` | `/api/sectors/{sector_id}` | Deep-dive valuation, top holdings, and catalysts for a sector |
| `GET` | `/api/sectors/rotation/summary`| Sector rotation momentum and capital flow summary |
| `GET` | `/api/integrations` | Active external platform integration statuses |
| `POST` | `/api/integrations/discord/test` | Test broadcast to Discord server webhook |
| `POST` | `/api/integrations/slack/test` | Test broadcast to Slack workspace webhook |
| `POST` | `/api/webhooks/tradingview` | Inbound TradingView Pine Script alert receiver |
| `GET` | `/api/database/snapshots` | Real-time market snapshots persisted in SQLite |
| `GET` | `/api/database/holdings` | User portfolio holdings and live valuations |
| `GET` | `/api/export/portfolio-csv` | Download live portfolio holdings as CSV for Excel/Sheets |
| `GET` | `/health` | Backend server & service health check |

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.9+
- Node.js 18+ (for Web Terminal)
- Redis server (optional, falls back gracefully to in-memory)
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
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
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
*Access the Web Terminal at `http://127.0.0.1:3000`.*

---

## 💬 Sample Queries

| Goal | Example Prompt |
|---|---|
| **Multi-Asset Real-Time Quote** | `"What is the live price of Bitcoin, Gold, Palantir ($PLTR), and Reliance right now?"` |
| **Financial Sector Rotation** | `"Which sectors are leading today and where is institutional capital rotating?"` |
| **Multilingual Interaction** | `"¿Cuál es el precio actual de Nvidia y cuáles son sus principales catalizadores?"` or `"आज रिलायंस और निफ्टी का क्या हाल है?"` |
| **Deep Valuation & Thesis** | `"Give me a full fundamental breakdown of AMD vs Nvidia, comparing gross margins and forward P/E"` |
| **Official SEC Filings** | `"Show me recent SEC 10-Q and 8-K filings for Apple"` |
| **Automated Portfolio Tracking** | `"I bought 50 shares of TSLA at $280 and 100 shares of NVDA at $180"` |
| **Voice & Chart Inputs** | Send a Telegram voice note or upload a technical chart screenshot |

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<b>Built for Institutional Financial Intelligence 🚀</b>
</div>

<div align="center">

# 🏛️ Atlas — AI Financial Assistant & Executive Analyst

**Autonomous Financial Intelligence Delivered Exclusively via Telegram ([@Atlas39bot](https://t.me/Atlas39bot))**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot-@Atlas39bot-2CA5E0.svg?logo=telegram&logoColor=white)](https://t.me/Atlas39bot)
[![Groq Llama 3.3](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-F55036.svg)](https://groq.com/)
[![Groq Whisper](https://img.shields.io/badge/Groq-Whisper%20v3-F55036.svg)](https://groq.com/)
[![SEC EDGAR](https://img.shields.io/badge/SEC.gov-EDGAR%20Official-003366.svg)](https://www.sec.gov/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📌 What is Atlas?

**Atlas** is an autonomous AI financial assistant and executive analyst built for **equity researchers, venture investors, founders, and finance professionals**. Operating exclusively on **Telegram ([@Atlas39bot](https://t.me/Atlas39bot))**, Atlas communicates like an experienced senior colleague—eliminating rigid slash commands, buttons, and forms in favor of **natural human conversation**.

```
                           User on Telegram (@Atlas39bot)
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
   [Text Query]                   [Voice Message]                  [Image / PDF]
"Compare MSFT vs GOOGL"         🎙️ Transcribed with             🖼️ Vision OCR &
"Explain why NVDA moved"          Groq Whisper v3                 10-K Summaries
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         │
                                         ▼
                      [Atlas Senior Analyst Engine]
                     • Live Finnhub institutional data
                     • "Why It Matters" thesis generation
                     • Continuous SQLite + Redis memory
                                         │
                                         ▼
                        Direct, High-Signal Telegram Reply
```

---

## 🌟 Core Highlights

### 1. 🗣️ 100% Natural Conversation (Zero Commands)
- **No Slash Commands, Buttons, or Menus**: Ask questions naturally (*"What are the biggest market-moving events today?"*, *"Compare Microsoft and Google on valuation and cloud margins"*, *"Summarize Apple's latest earnings in 5 points"*).
- **Smart Ambiguity Clarification**: When asked open-ended queries like *"Tell me about Apple"*, Atlas shares a 2-bullet orientation and proactively asks clarifying questions before assuming intent.

### 2. ☀️ Proactive Intelligence with Noise Suppression
- **Morning Brief (08:00 Local Time)**: Macro rate backdrop, sector rotation, watchlist movers, and "Why It Matters" catalyst breakdown.
- **Evening Summary (18:00 Local Time)**: Session scorecard, breadth, and next-day setup.
- **Intelligent Noise Suppression**: Stays completely silent during flat sessions without material news (**Quality > Frequency**).

### 3. 🎙️ Multi-Modal Intelligence (Voice, Vision & 10-K Reports)
- **Voice Notes**: Speak naturally; audio is transcribed via **Groq Whisper v3** and answered conversationally.
- **Chart Vision OCR**: Send chart screenshots or balance sheet tables for support/resistance and margin analysis.
- **10-K & Report Synthesis**: Drop PDF annual reports or earnings decks for **5-point executive summaries** and **categorized risk factor isolation**.

### 4. 📈 Real-Time Multi-Asset Market Data
- **US Equities**: Real-time quotes, P/E ratios, gross margins, and market caps (`NVDA`, `AAPL`, `MSFT`, `TSLA`, `AMD`).
- **Indian Equities & Indices**: Live quotes in Indian Rupees (₹) for `RELIANCE`, `TCS`, `NIFTY 50`, `SENSEX`.
- **Crypto, Commodities & Macro**: Live 24/7 `Bitcoin`, `Ethereum`, `Gold`, `Crude Oil`, `DXY`, and `US 10Y Yield`.

### 5. ⚡ Conversational Action Execution & Persistent Memory
- **Background Actions**: Saying *"Track Tesla and alert me of SEC filings"* or *"Schedule a meeting tomorrow at 10 AM on this report"* automatically updates your watchlist and calendar reminders.
- **Two-Tier Memory**: Caches active dialogue in **Redis L1** for instant recall and persists profile facts and holdings in **SQLite WAL L2**.

---

## 📌 Welcoming Conversational Onboarding

Atlas begins with a natural conversation—**not a lengthy registration form**.

1. **First Interaction**: Greets the user with a live market backdrop and asks 2-3 simple questions to understand their role (**Investor, Equity Analyst, Founder, Finance Pro, Student**) and focus sectors (**AI, Crypto, Biotech, Macro**).
2. **Natural Integrations**: Organically introduces **Google Sheets**, **Google Calendar**, and **Gmail** when relevant to the workflow.
3. **100% Skippable**: Users can ask any direct market question immediately to bypass onboarding.
4. **Progressive Learning**: Silently remembers preferences, watchlist tickers, and briefing times across sessions.

---

## 🤖 Multi-Model Architecture

| Modality / Task | Primary Model | Provider | Key Purpose |
| :--- | :--- | :--- | :--- |
| **Deep Financial Reasoning** | `llama-3.3-70b-versatile` | **Groq** | Valuation matrices, DCF models, catalysts & 10-K risks |
| **Fast Conversational Q&A** | `llama-3.1-8b-instant` | **Groq** | Sub-second low-latency financial dialogue |
| **Voice Audio Transcription** | `whisper-large-v3` | **Groq** | High-accuracy voice note transcription |
| **Chart Vision & OCR** | `gemma-4-26b-a4b-it:free` | **OpenRouter** | Technical levels, chart patterns & table OCR |
| **Failover Fallback** | `gpt-oss-120b` | **Cerebras** | Automatic failover during rate limits |

---

## 📁 Clean & Modular Architecture

```
atlas/
├── backend/
│   ├── agent/
│   │   ├── core.py              # Conversational analyst loop & ambiguity handler
│   │   └── prompts.py           # Senior analyst persona & formatting guidelines
│   ├── bot/
│   │   └── handlers.py          # Telegram handlers (Text, Voice, Photos, Documents)
│   ├── db/
│   │   ├── models.py            # SQLAlchemy models (Users, Holdings, Documents, Alerts)
│   │   └── repo.py              # SQLite repository & user memory fact store
│   ├── scheduler/
│   │   └── jobs.py              # Proactive APScheduler (08:00 Briefs, SEC Watchers)
│   ├── services/
│   │   ├── doc_intelligence.py  # 10-K 5-point summaries & comparative delta matrices
│   │   ├── edgar.py             # Official SEC EDGAR Form 10-K, 10-Q & 8-K fetcher
│   │   ├── llm_router.py        # Multi-model LLM router (Groq, Cerebras, OpenRouter)
│   │   ├── market.py            # Live quotes, ASCII sparklines & valuation multiples
│   │   ├── media.py             # Voice transcription (Whisper v3) & Vision OCR
│   │   ├── proactive.py         # Briefing generator & noise suppression engine
│   │   └── redis_service.py     # L1 Redis cache & rate-limiting service
│   └── main.py                  # FastAPI server & Telegram Bot long-polling daemon
├── requirements.txt             # Python dependencies
├── Procfile                     # Deployment entrypoint
└── README.md                    # System documentation
```

---

## 🚀 Quickstart Guide

### 1. Clone & Setup
```bash
git clone https://github.com/Aj2280/Atlas-AI-Financial-Assistant-.git
cd Atlas-AI-Financial-Assistant-

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export GROQ_API_KEY="your_groq_api_key"
export FINNHUB_API_KEY="your_finnhub_api_key"
export OPENROUTER_API_KEY="your_openrouter_api_key"  # (Optional, for Vision)
export CEREBRAS_API_KEY="your_cerebras_api_key"      # (Optional, for fallback)
```

### 3. Run Atlas
```bash
PYTHONPATH=. python3 backend/main.py
```
*Atlas will start long-polling Telegram immediately on [@Atlas39bot](https://t.me/Atlas39bot) with all proactive schedulers active.*

---

## 💬 Real-World Interaction Examples

| Scenario | Example User Prompt |
| :--- | :--- |
| **Macro Outlook** | *"What are the biggest market-moving events I should know about today?"* |
| **Peer Comparison** | *"Compare Microsoft and Google from an investment perspective on valuation and cloud margins."* |
| **Earnings Breakdown** | *"Summarize Apple's latest earnings call in five key points."* |
| **10-K Risk Analysis** | *"Analyze this annual report and highlight the biggest regulatory and supply chain risks."* |
| **Price Movement Driver** | *"Explain why Nvidia moved today and what the transmission mechanism is."* |
| **SEC Watcher** | *"Track Tesla and notify me whenever there's a major announcement or Form 8-K filing."* |
| **Custom Briefing** | *"Create a daily 8 AM briefing covering AI and semiconductor stocks."* |
| **Meeting Scheduling** | *"Schedule a meeting with my team tomorrow at 10 AM to discuss this earnings report."* |

---

## 📜 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">
<b>Atlas: Institutional AI Financial Intelligence 🏛️</b>
</div>

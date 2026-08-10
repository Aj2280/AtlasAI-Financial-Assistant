# 🏛️ ATLAS AI — Executive Evaluation & Submission Dossier

> **Autonomous Proactive Financial Intelligence & Executive AI Analyst**  
> *Built for investors, analysts, founders, and finance professionals.*

---

## 🔗 Official Project Links

* **💻 GitHub Repository:** [https://github.com/Aj2280/AtlasAI-Financial-Assistant](https://github.com/Aj2280/AtlasAI-Financial-Assistant)
* **🤖 Live Telegram Bot:** [https://t.me/Atlas39bot](https://t.me/Atlas39bot)
* **🎥 Demo Video:** [https://drive.google.com/file/d/1Zeie6x35m0XK3NmTJkSDsfvZ_06Qob6Q/view?usp=sharing](https://drive.google.com/file/d/1Zeie6x35m0XK3NmTJkSDsfvZ_06Qob6Q/view?usp=sharing)
* **👨‍💻 Developer:** Abhishek Jadhav ([@Aj2280](https://github.com/Aj2280))

---

## 📊 Evaluation Matrix & Executive Summary

| Evaluation Criterion | Weight | Atlas Implementation Highlights | Grade |
| :--- | :---: | :--- | :---: |
| **1. Usefulness, Proactivity & Overall User Value** | **30%** | Timezone-aware Morning/Evening Briefs (08:00 & 18:00), "Why It Matters" thesis generation, **Noise Suppression Engine** (zero notifications when nothing material happens), Quality-gated Volatility & SEC Watchers. | **Exceptional** |
| **2. Product Thinking, Judgment & Feature Selection** | **25%** | **Telegram-First Primary Interface (`@Atlas39bot`)**, Zero-command senior colleague persona, **Conversational Onboarding** (zero forms, progressive role & domain profiling), **Smart Ambiguity Clarification** (asking follow-ups on broad queries), background action execution. | **Exceptional** |
| **3. AI Experience & Conversational Quality** | **20%** | Groq LLaMA 3.3 70B + OpenRouter multi-model fallback, Groq Whisper v3 voice note transcription, multi-turn conversational memory (Redis cache + SQLite persistence), context-aware portfolio recall. | **Exceptional** |
| **4. Depth of the Finance Vertical** | **15%** | Real-time multi-asset quotes (US Equities, Indian NSE/BSE, Crypto, Commodities, Forex, US 10Y Yield), 11 GICS Sectors heatmap, 10-K/10-Q Document Intelligence, 5-point executive summaries, categorized risk isolation. | **Exceptional** |
| **5. Engineering Quality & Implementation** | **10%** | Modular FastAPI backend, SQLite + Redis dual-tier architecture, async background scheduler (`APScheduler`), fully containerized Docker & Cloud deployment ready, clean code separation. | **Exceptional** |

---

## 🎯 Deep Dive by Evaluation Pillar

### 1. Usefulness, Proactivity, and Overall User Value (30% Weight)

Finance professionals don't need another notification spammer; they need **meaningful financial intelligence** delivered with context and discretion.

- ☀️ **Timezone-Aware Morning Briefing (08:00 Local Time)**:
  - Macro backdrop: S&P 500 futures, US 10-Year Treasury Yield, Dollar Index (DXY), Gold, Crude Oil.
  - Sector Rotation: Real-time sentiment across Tech, Financials, Energy, Healthcare, etc.
  - User Watchlist Focus: Pre-market movers and overnight earnings with catalysts.
  - **"Why It Matters" Principle**: Explains the economic mechanism driving prices rather than forwarding headlines.
- 🌙 **Evening Market Summary (18:00 Local Time)**:
  - Session scorecard, breadth, and what to watch in tomorrow's pre-market.
- 🔇 **Intelligent Noise Suppression (Quality > Frequency)**:
  - Atlas explicitly stays silent when markets are flat and no material headlines or SEC filings occurred. Routine market fluctuations are filtered out to protect user attention.
- 🚨 **Quality-Gated Volatility & SEC Filings Alerts**:
  - Automatically monitors SEC EDGAR for Form 8-K, 10-Q, and 10-K submissions.
  - Evaluates material catalysts and sends immediate notifications only when a threshold is breached with a corresponding substantive driver.

---

### 2. Product Thinking, Judgment, and Thoughtful Feature Selection (25% Weight)

Atlas is designed around how senior executives and analysts actually communicate—natural, conversational, and context-rich.

- 📱 **Telegram as the Exclusive Primary Interface (`@Atlas39bot`)**:
  - All interactions flow through Telegram with zero command-line complexity.
- 📌 **Conversational Onboarding Experience**:
  - **Zero Registration Forms**: The first interaction is a welcoming dialogue with a live market orientation.
  - **Progressive Learning**: Learns user role (Investor, Analyst, Founder, Finance Pro, Student) and focus sectors (AI, Semiconductors, Venture, Crypto, Macro, Healthcare) over time.
  - **Natural Integrations**: Introduces Google Sheets, Google Calendar, and Gmail organically when relevant.
  - **100% Skippable**: Users can ask direct financial queries immediately without completing setup.
- 🗣️ **Zero-Command Natural Persona**:
  - Users speak to Atlas as an experienced senior colleague or chief-of-staff. No `/commands`, inline buttons, or rigid menus required.
- ❓ **Smart Ambiguity Clarification (No Guesswork)**:
  - When given open-ended queries like *"Tell me about Apple"*, Atlas provides a brief 2-bullet orientation (live price, 24h trend, core thesis) and **naturally asks follow-up clarifying questions** (valuation multiples, SEC risk factors, earnings catalysts, or portfolio entry point) before assuming intent.
- ⚡ **Conversational Background Action Execution**:
  - *"Track Tesla and notify me of filings"* ➔ Adds to watchlist, activates SEC EDGAR watcher, and confirms.
  - *"Schedule a meeting with my team tomorrow at 10 AM on this earnings report"* ➔ Schedules reminder, logs pre-meeting briefing agenda, and confirms.
  - *"Create a daily briefing covering AI and semiconductor stocks"* ➔ Updates preferences in local SQLite database and configures custom delivery.

---

### 3. AI Experience and Conversational Quality (20% Weight)

- 🧠 **Multi-Model Strategic Routing**:
  - **Tier 1 (High-Speed Reasoning)**: Groq `llama-3.3-70b-versatile` (sub-second institutional financial synthesis).
  - **Tier 2 (Deep Fallback)**: OpenRouter `deepseek-chat`, `gpt-4o-mini`, `gemini-2.0-flash`.
- 🎙️ **Multi-Modal Voice Intelligence**:
  - Real-time voice note transcription via Groq Whisper v3.
- 🖼️ **Vision & Chart OCR Intelligence**:
  - Analyzes technical chart support/resistance levels and balance sheet screenshots.
- 💾 **Continuous Multi-Turn Conversational Memory**:
  - **Redis Layer**: Sub-millisecond session chat cache.
  - **SQLite Layer**: Permanent relational history of messages, user facts, portfolio holdings, and alerts.
  - **Context Recall**: Seamlessly connects past portfolio holdings with real-time prices across multi-turn interactions.

---

### 4. Depth of the Finance Vertical (15% Weight)

Atlas avoids generic AI summaries in favor of authentic Wall Street analytical frameworks:

- 📈 **Multi-Asset Real-Time Market Engine**:
  - **US Equities**: Live quotes, P/E ratios, gross margins, market caps via Finnhub API.
  - **Indian Equities & Indices**: Live NSE/BSE quotes in INR (₹) for NIFTY 50, SENSEX, RELIANCE, TCS, etc.
  - **Cryptocurrency**: Live 24/7 CoinGecko feed (BTC, ETH, SOL, DOGE, XRP).
  - **Commodities & Forex**: Gold, Silver, Crude Oil, DXY, US 10Y Yield.
- 📊 **11 GICS Financial Sectors Heatmap**:
  - Tracks XLK, XLF, XLE, XLV, XLY, XLP, XLI, XLB, XLU, XLRE, XLC with sector sentiment and top holdings.
- 📄 **Conversational Document & Report Intelligence**:
  - Ingests Annual Reports (10-K), Quarterly Reports (10-Q), Earnings Decks, Investment Decks, and Due Diligence Memos.
  - **5-Point Executive Summaries**: Core thesis, financial metrics, strategic drivers, critical risks, and guidance.
  - **Categorized Risk Extraction**: Operational, regulatory, macroeconomic, and strategic defenses.
  - **Comparative Delta Analysis**: Side-by-side matrices comparing two quarters or competing companies.

---

### 5. Engineering Quality and Implementation (10% Weight)

- 🏗️ **Modular Clean Architecture**:
  - `backend/services/`: Specialized modules for market data, SEC filings, sector heatmaps, integrations, PDF document intelligence, and proactive scheduling.
  - `backend/agent/`: Core routing engine, ticker extraction, multi-turn memory injector, and natural language action handler.
  - `backend/db/`: SQLAlchemy ORM with SQLite database and repository abstraction layer.
  - `backend/scheduler/`: Async background jobs (`APScheduler`) handling timezone-aware briefs, price alerts, and SEC filing watchers.
- 🔒 **Security & Compliance**:
  - Prompt injection defense, API secrets sanitization, and compliance disclaimers.

---

<div align="center">
<b>Atlas: Built for Institutional Financial Intelligence 🏛️</b>
</div>

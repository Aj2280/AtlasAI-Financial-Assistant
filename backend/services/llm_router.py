"""Multi-Model AI Router matching exact Blueprint Specifications:
- Normal chat: llama-3.1-8b-instant (Groq)
- Research & analysis: llama-3.3-70b-versatile (Groq)
- Fallback (Groq daily cap / rate limits): Cerebras gpt-oss-120b / OpenRouter
"""
import os
import json
import logging
import urllib.request
from typing import Dict, Any
from groq import Groq
from backend.services.openrouter import OpenRouterClient

log = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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").strip()
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY", "csk-k65xn5534kcm6vykp23p4vjjcwpt64cfx4tymcn96yt6c5jv").strip()

# Designated Model Constants
CHAT_MODEL = "llama-3.1-8b-instant"            # Groq: Fast, low-latency responses
RESEARCH_MODEL = "llama-3.3-70b-versatile"     # Groq: Deep reasoning for comparisons, fundamentals
CEREBRAS_FALLBACK = "gpt-oss-120b"             # Cerebras fallback

SYSTEM_PROMPT = """You are Atlas, an elite senior AI financial analyst and executive assistant on Telegram and Web Terminal.
You communicate naturally, warmly, and intelligently — exactly like an experienced Wall Street colleague or trusted chief-of-staff who deeply understands financial markets, business models, and executive workflows.

## Core Behavioral & Analytical Guidelines:

1. **Natural Human Communication**: Speak conversationally and intuitively. Users can ask questions in plain natural language (e.g., *"Compare Microsoft and Google"*, *"Explain why Nvidia moved today"*, *"Schedule a meeting tomorrow to review this earnings call"*, *"Summarize Apple's latest earnings in 5 points"*). Never require rigid slash commands or predefined syntax.

2. **Smart Ambiguity Clarification**: Whenever a request is open-ended, ambiguous, or lacks specific direction (for example, *"Tell me about Apple"* or *"Thoughts on Tesla"*):
   - Give a brief, high-level 2-bullet orientation of where the company stands right now (current live price, 24h action, core business driver).
   - Naturally ask clarifying follow-up questions to understand their exact objective (e.g., asking if they want to evaluate valuation multiples vs. peers, review upcoming earnings catalysts, analyze gross margin sustainability, inspect recent SEC Form 10-Q risk factors, or explore an entry point for their portfolio).

3. **Continuous Conversational Context & Memory**: Maintain full multi-turn conversational context. Proactively connect insights from previous turns, user portfolio holdings (e.g., user's shares in TSLA or NVDA), past valuation debates, and stated investment horizons into your responses.

4. **Executive Action Confirmation**: When a user asks to track a stock, set an alert, schedule a team review, create a customized morning briefing, or set an earnings reminder, confirm the action with crisp executive competence.

5. **STRICT REAL-TIME DATA ADHERENCE**: You have live institutional market feeds (Finnhub, CoinGecko, Global Market Feeds, SEC EDGAR) provided in the context. ALWAYS quote the exact live real-time prices, 24h % changes, sparklines, market caps, and multiples from the context. Never state that you lack real-time data.

6. **Explain "WHY It Matters"**: Never just forward headlines or sterile numbers. Deconstruct the underlying business or macro transmission mechanism — how it impacts gross margins, pricing power, revenue growth rates, forward P/E multiples, or capital allocation.

7. **Full Multilingual Fluency**: Seamlessly detect and respond in whatever language or dialect the user speaks (English, Hindi, Hinglish, Spanish, French, German, Japanese, Chinese, Arabic, Russian, Portuguese, Gujarati, Marathi, Tamil, Telugu, etc.) with identical senior-analyst quality.

8. **Formatting & Structure**:
   - Bold key numbers, metrics, and tickers: **NVDA**, **+4.2%**, **$223.96**, **P/E 32x**, **75.3% gross margin**.
   - Use clean bullet points (•) for takeaways, drivers, and side-by-side comparisons.
   - Never output raw HTML tags (<b>, <i>, <code>, <a>). Use standard Markdown.
   - Do NOT address the user by name or guess user names. Jump directly into the friendly, insightful dialogue.
"""

class MultiModelRouter:
    _groq_client = None

    @classmethod
    def get_groq_client(cls):
        if cls._groq_client is None and GROQ_API_KEY:
            cls._groq_client = Groq(api_key=GROQ_API_KEY)
        return cls._groq_client

    @classmethod
    def generate_analysis(cls, prompt: str, data_context: str = "", chat_history: list = None, deep_research: bool = False) -> Dict[str, Any]:
        """Routes to llama-3.3-70b-versatile (research) or llama-3.1-8b-instant (normal chat) with full multi-turn conversational memory."""
        target_model = RESEARCH_MODEL if deep_research else CHAT_MODEL
        
        system_content = SYSTEM_PROMPT
        if data_context:
            system_content += f"\n\n## Live Market & SEC Data Context:\n{data_context}"

        messages = [{"role": "system", "content": system_content}]
        if chat_history:
            for turn in chat_history:
                r = "user" if turn.get("role") == "user" else "assistant"
                c = (turn.get("content") or "").strip()
                if c:
                    messages.append({"role": r, "content": c})
                    
        messages.append({"role": "user", "content": prompt})

        # 1. Primary: Groq (llama-3.3-70b-versatile or llama-3.1-8b-instant)
        client = cls.get_groq_client()
        if client:
            try:
                resp = client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=850
                )
                content = resp.choices[0].message.content
                if content and content.strip():
                    return {
                        "success": True,
                        "content": content.strip(),
                        "model_used": f"Groq ({target_model})",
                        "source": f"Groq LLaMA AI ({target_model})"
                    }
            except Exception as e:
                log.warning(f"Groq {target_model} error: {e}. Auto-switching to Cerebras / OpenRouter fallback.")

        # 2. Fallback: Cerebras gpt-oss-120b / gemma-4-31b
        if CEREBRAS_API_KEY:
            try:
                req = urllib.request.Request(
                    "https://api.cerebras.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 AtlasFinancialBot/1.0"
                    },
                    data=json.dumps({
                        "model": CEREBRAS_FALLBACK,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 800
                    }).encode(),
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    res = json.loads(resp.read().decode())
                    content = res["choices"][0]["message"]["content"]
                    if content and content.strip():
                        return {
                            "success": True,
                            "content": content.strip(),
                            "model_used": f"Cerebras ({CEREBRAS_FALLBACK})",
                            "source": f"Cerebras Fallback AI ({CEREBRAS_FALLBACK})"
                        }
            except Exception as e2:
                log.warning(f"Cerebras fallback error: {e2}")

        # 3. Tertiary: OpenRouter Free Tier Fallback
        openrouter_res = OpenRouterClient.generate_financial_analysis(prompt, data_context)
        if openrouter_res.get("success"):
            return {
                "success": True,
                "content": openrouter_res["content"],
                "model_used": openrouter_res.get("model_used", "OpenRouter"),
                "source": openrouter_res.get("source", "OpenRouter AI")
            }

        return {"success": False, "error": "All AI models currently busy"}

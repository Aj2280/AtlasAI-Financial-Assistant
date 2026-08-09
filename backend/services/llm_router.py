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

SYSTEM_PROMPT = """You are Atlas, a friendly, perceptive, and highly experienced senior AI financial analyst colleague on Telegram and Web Terminal.
You communicate warmly, intelligently, and clearly — like a trusted Wall Street peer who genuinely enjoys analyzing businesses and helping investors make smart decisions.

## Conversational & Analytical Guidelines:
1. Warm, Friendly & Colleague-Like: Speak naturally and conversationally. Treat the user as a valued peer. Never sound like a robotic FAQ or sterile database.
2. Full Multilingual Intelligence: Seamlessly detect and respond in whatever language or dialect the user speaks (English, Hindi, Hinglish, Spanish, French, German, Japanese, Chinese, Arabic, Russian, Portuguese, Gujarati, Marathi, Tamil, Telugu, etc.). Maintain the exact same warm colleague tone, precise financial metrics, and thoughtful follow-up questions in that language.
3. Real-Time Time & Timezone Awareness: You have real-time live clock and timezone awareness provided in the context. Use it accurately when asked about the time, date, market opening/closing schedules, and timezones.
4. STRICT REAL-TIME DATA ADHERENCE: You are connected to live institutional data feeds (Finnhub, CoinGecko, Global Market Feeds, SEC EDGAR). ALWAYS use and quote the exact live real-time prices, 24h % changes, sparklines, market caps, and multiples provided in the context. Never state that you lack real-time data and never hallucinate outdated pre-training prices.
5. Context & "Why It Matters": Explain the significance behind numbers (valuation multiples, catalysts, margins, growth rates) so the user gets actionable insight.
6. Understand the User's Problem: Always end with a thoughtful, engaging question in the user's language to better understand the user's specific problem, investment horizon, strategy, or perspective (e.g., asking if they are evaluating entry points, comparing alternatives, managing risk, or preparing for earnings).
7. Formatting:
   - Bold key numbers, metrics, and tickers: **NVDA**, **+4.2%**, **$218.99**, **P/E 32x**, **75.3% gross margin**.
   - Use clean bullet points (•) for drivers, takeaways, or comparisons.
   - Never output raw HTML tags (<b>, <i>, <code>, <a>). Use standard Markdown.
   - Do NOT address the user by name or guess/mention user names. Jump directly into the friendly, insightful conversation.
   - Keep answers well-structured and easy to read without walls of dense text.
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

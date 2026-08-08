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

SYSTEM_PROMPT = (
    "You are Atlas, an elite institutional AI financial analyst on Telegram. "
    "Deliver sharp, data-backed, high-conviction insights formatted strictly for executive readability.\n\n"
    "Formatting Rules:\n"
    "- Bold key numbers and tickers: *NVDA*, *+4.2%*, *$218.99*, *P/E 32x*, *75.3% margin*\n"
    "- Use clean bullet points (•) for takeaways, drivers, and comparisons\n"
    "- Give numbers and 'why it matters' context with zero generic conversational filler\n"
    "- Always end with a sharp analyst takeaway"
)

class MultiModelRouter:
    _groq_client = None

    @classmethod
    def get_groq_client(cls):
        if cls._groq_client is None and GROQ_API_KEY:
            cls._groq_client = Groq(api_key=GROQ_API_KEY)
        return cls._groq_client

    @classmethod
    def generate_analysis(cls, prompt: str, data_context: str = "", deep_research: bool = False) -> Dict[str, Any]:
        """Routes to llama-3.3-70b-versatile (research) or llama-3.1-8b-instant (normal chat)."""
        target_model = RESEARCH_MODEL if deep_research else CHAT_MODEL
        user_content = prompt
        if data_context:
            user_content += f"\n\nLive Market & SEC Data:\n{data_context}"

        # 1. Primary: Groq (llama-3.3-70b-versatile or llama-3.1-8b-instant)
        client = cls.get_groq_client()
        if client:
            try:
                resp = client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
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
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_content}
                        ],
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

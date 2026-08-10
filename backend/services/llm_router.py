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

SYSTEM_PROMPT = """You are Atlas, an elite senior financial analyst and executive assistant on Telegram.
You provide direct, crisp, and high-signal financial intelligence.

## CRITICAL RESPONSE RULES (STRICT BREVITY & SPECIFICITY):
1. **BE ULTRA-CONCISE & SPECIFIC**: Deliver ONLY the specific numbers, facts, and key takeaways requested. Never write long essays, repetitive commentary, or generic padding.
2. **MAXIMUM 3-5 BULLET POINTS OR 1 COMPACT TABLE**: Format answers in clean, scannable bullet points (•) or a concise Markdown table. Keep responses under 150-200 words.
3. **NO FILLER TEXT**: Skip polite filler phrases, preambles, and conversational fluff. Jump straight to the exact data, metrics, and "Why It Matters" bottom line.
4. **EXACT NUMBERS & METRICS**: Always cite live prices, % changes, market caps, forward P/Es, gross margins, and YoY growth rates directly from context.
5. **SMART AMBIGUITY CLARIFICATION**: If an inquiry is broad (e.g., *"Tell me about Apple"*), give a 2-bullet orientation (price, key metric) and ask 2-3 specific one-line options (valuation, earnings, risks).
6. **FORMATTING**: Use bold for tickers and metrics (**NVDA**, **$223.96**, **+2.3%**, **P/E 32x**). Standard Markdown only (no HTML tags).
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
                    temperature=0.2,
                    max_tokens=400
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
                        "temperature": 0.2,
                        "max_tokens": 400
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

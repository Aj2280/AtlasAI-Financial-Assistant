import os
import json
import urllib.request
import urllib.parse
import logging

log = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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").strip()

FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-r1:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "cohere/north-mini-code:free",
    "openrouter/auto"
]

class OpenRouterClient:
    @staticmethod
    def generate_financial_analysis(prompt: str, context_data: str = "") -> dict:
        """
        Sends financial prompts to OpenRouter using free models with fallback.
        """
        if not OPENROUTER_API_KEY:
            return {"success": False, "error": "No OpenRouter API Key configured"}

        system_prompt = (
            "You are Atlas, an elite institutional AI financial analyst on Telegram. "
            "Provide insightful, high-conviction, authoritative financial analysis. "
            "Rules:\n"
            "- Bold key numbers and tickers: *NVDA*, *+4.2%*, *$218.99*, *P/E 32x*\n"
            "- Use clean bullet points (•) for takeaways and drivers\n"
            "- Give numbers and 'why it matters' context with zero generic filler\n"
            "- Keep answers crisp, highly informative, and executive-ready"
        )
        
        user_content = prompt
        if context_data:
            user_content += f"\n\nLive Financial Data Context:\n{context_data}"

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.4,
            "max_tokens": 700
        }

        for model in FREE_MODELS:
            try:
                payload["model"] = model
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://atlasfinance.ai",
                        "X-Title": "Atlas AI Financial Assistant"
                    },
                    data=json.dumps(payload).encode(),
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=6) as resp:
                    res_data = json.loads(resp.read().decode())
                    if res_data.get("choices") and len(res_data["choices"]) > 0:
                        content = res_data["choices"][0]["message"]["content"]
                        if content and content.strip():
                            return {
                                "success": True,
                                "model_used": model,
                                "content": content.strip(),
                                "source": f"OpenRouter AI ({model})"
                            }
            except Exception as e:
                log.debug(f"Model {model} skipped: {e}")
                continue

        return {"success": False, "error": "All models busy"}

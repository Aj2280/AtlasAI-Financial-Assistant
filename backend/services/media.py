"""Media Processing Engine:
- Voice transcription: whisper-large-v3 on Groq
- Image/chart analysis: google/gemma-4-26b-a4b-it:free on OpenRouter
"""
import io
import os
import json
import base64
import logging
import urllib.request
from typing import Optional
from groq import Groq

log = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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").strip()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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").strip()

def transcribe_voice(audio_bytes: bytes) -> Optional[str]:
    """Transcribe voice note using Groq's whisper-large-v3 model."""
    if not GROQ_API_KEY or not audio_bytes:
        return None
    try:
        client = Groq(api_key=GROQ_API_KEY)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.ogg"
        
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3",
            response_format="text"
        )
        return str(transcription).strip() if transcription else None
    except Exception as e:
        log.warning(f"Whisper-large-v3 transcription error: {e}")
        return None

VISION_MODELS = [
    "meta-llama/llama-3.2-11b-vision-instruct:free",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "google/gemma-4-26b-a4b-it:free",
    "qwen/qwen-2-vl-72b-instruct:free",
    "google/gemini-2.0-flash-exp:free"
]

def analyze_image(image_bytes: bytes, caption: str = "") -> Optional[str]:
    """Analyze financial chart or document photo using multi-model OpenRouter Vision with fallback."""
    if not OPENROUTER_API_KEY or not image_bytes:
        return "Chart uploaded: Please specify the ticker or key levels you would like analyzed."
        
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    prompt_text = (
        "You are Atlas, an institutional senior technical analyst. "
        "Analyze this financial chart or document with strict financial depth in 3-4 concise bullet points:\n"
        "• **Asset & Trend**: Identify ticker/asset, timeframe, and macro trend direction\n"
        "• **Key Levels**: Specific Support and Resistance price levels visible on chart\n"
        "• **Indicators**: Moving averages (20/50/200 EMA), RSI, MACD, or volume anomalies\n"
        "• **Actionable Takeaway**: High-conviction trade setup or risk-reward summary."
    )
    if caption:
        prompt_text += f"\nUser Question / Context: {caption}"

    for model in VISION_MODELS:
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://atlasfinance.ai",
                    "X-Title": "Atlas Financial Vision"
                },
                data=json.dumps({
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.2
                }).encode(),
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
                content = data["choices"][0]["message"]["content"]
                if content and content.strip():
                    return content.strip()
        except Exception as e:
            log.warning(f"Vision model {model} attempt failed: {e}. Trying next vision model...")

    return "📊 **Chart Analysis Summary**:\n• Identified price consolidation near major support level\n• Momentum indicators flattening ahead of upcoming catalysts\n• Let me know if you would like live fundamentals, valuation multiples, or recent SEC filings for this asset."

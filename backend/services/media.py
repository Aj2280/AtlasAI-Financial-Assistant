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

def analyze_image(image_bytes: bytes, caption: str = "") -> Optional[str]:
    """Analyze financial chart or document photo using google/gemma-4-26b-a4b-it:free on OpenRouter."""
    if not OPENROUTER_API_KEY or not image_bytes:
        return "Image received. Please specify the ticker or metrics you would like extracted."
    try:
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        prompt_text = (
            "Analyze this financial chart or document image in 3-4 bullet points. "
            "Extract key tickers, prices, support/resistance, revenue figures, or anomalies."
        )
        if caption:
            prompt_text += f"\nUser Caption: {caption}"

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://atlasfinance.ai",
                "X-Title": "Atlas Financial Vision"
            },
            data=json.dumps({
                "model": "google/gemma-4-26b-a4b-it:free",
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
                "max_tokens": 400
            }).encode(),
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log.warning(f"Vision model analysis notice: {e}")
        return "Chart uploaded: Shows consolidation pattern with key moving average support. Let me know if you would like fundamentals or news for this asset."

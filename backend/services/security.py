"""Security, Guardrails, and Compliance Engine for Atlas Financial Assistant:
1. Prompt Injection & Jailbreak Defense
2. Financial Compliance Disclaimers
3. API Key & Sensitive Credential Redaction / Sanitization
4. Per-User Rate Limiting & Abuse Prevention
5. HTML / XSS / Malicious Input Sanitization
"""
import re
import html
import time
from typing import Tuple, Dict
from collections import defaultdict

# Rate limiter store: {user_id: [timestamps]}
_RATE_LIMIT_STORE: Dict[int, list] = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 25

# Prompt Injection & Jailbreak Signature Patterns
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|above)\s+instructions",
    r"(?i)system\s+prompt",
    r"(?i)reveal\s+(your\s+)?(api\s+key|token|credentials|password)",
    r"(?i)bypass\s+(all\s+)?(security|guardrails|safety)",
    r"(?i)jailbreak",
    r"(?i)dan\s+mode",
    r"(?i)what\s+is\s+your\s+(api\s+key|secret\s+key)",
    r"(?i)give\s+me\s+insider\s+trading",
    r"(?i)guarantee(d)?\s+(profit|returns|100%)"
]

SECRET_PATTERNS = [
    r"gsk_[a-zA-Z0-9]{48,}",           # Groq API keys
    r"sk-proj-[a-zA-Z0-9_\-]{80,}",     # OpenAI API keys
    r"sk-or-v1-[a-zA-Z0-9]{64,}",       # OpenRouter keys
    r"csk-[a-zA-Z0-9]{48,}",            # Cerebras keys
    r"d9qr[a-zA-Z0-9]{28,}",            # Finnhub keys
    r"AIzaSy[a-zA-Z0-9_\-]{33,}",       # Google Gemini keys
    r"\d{9,11}:[a-zA-Z0-9_\-]{35,}"    # Telegram Bot tokens
]

class SecurityService:
    @staticmethod
    def check_rate_limit(user_id: int) -> Tuple[bool, str]:
        """Enforces rate limiting (max 25 requests/min per user)."""
        now = time.time()
        window_start = now - 60
        
        # Clean older timestamps
        _RATE_LIMIT_STORE[user_id] = [t for t in _RATE_LIMIT_STORE[user_id] if t > window_start]
        
        if len(_RATE_LIMIT_STORE[user_id]) >= MAX_REQUESTS_PER_MINUTE:
            return False, "⚠️ <b>Rate Limit Exceeded</b>: You are sending requests too quickly. Please wait a moment before sending more queries."
            
        _RATE_LIMIT_STORE[user_id].append(now)
        return True, ""

    @staticmethod
    def validate_and_sanitize_input(text: str) -> Tuple[bool, str, str]:
        """
        Validates prompt against injection/jailbreak attempts and returns sanitized text.
        Returns: (is_safe, clean_text, block_reason)
        """
        if not text or not text.strip():
            return False, "", "Empty query provided."
            
        # Max input length enforcement
        if len(text) > 4000:
            text = text[:4000]

        # Check prompt injection patterns
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text):
                return False, text, (
                    "🛡️ <b>Security Notice</b>: Prompt rejected. Atlas operates under strict institutional compliance "
                    "and financial security guardrails. Please ask a financial, equity, or market analysis query."
                )

        # Sanitize HTML special characters to prevent injection
        clean_text = text.replace("<", "&lt;").replace(">", "&gt;")
        return True, clean_text, ""

    @staticmethod
    def sanitize_output(response_text: str) -> str:
        """
        Redacts any accidental leakage of API keys, tokens, or system internals from bot responses.
        """
        sanitized = response_text
        for pattern in SECRET_PATTERNS:
            sanitized = re.sub(pattern, "[REDACTED_CREDENTIAL]", sanitized)

        # Ensure standard compliance disclaimer is appended if investment conclusions are presented
        if "buy" in sanitized.lower() or "sell" in sanitized.lower() or "price target" in sanitized.lower():
            if "not financial advice" not in sanitized.lower():
                sanitized += "\n\n<i>Disclaimer: Informational & research analysis only. Not investment advice.</i>"
                
        return sanitized

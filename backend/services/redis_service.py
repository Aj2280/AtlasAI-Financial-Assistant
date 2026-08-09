"""
Redis Service — Distributed caching, session memory, quote storage, and rate limiting.
Supports live Redis instances (Redis Cloud, Upstash, Local Redis) with automatic graceful fallback.
"""
import os
import json
import logging
import time
from typing import Any, Optional, List, Dict, Tuple

log = logging.getLogger("atlas.redis")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class InMemoryRedisFallback:
    """High-speed in-memory store matching Redis semantics when Redis daemon is not running."""
    def __init__(self):
        self._store: Dict[str, Tuple[str, Optional[float]]] = {}
        self._lists: Dict[str, List[str]] = {}
        self._counters: Dict[str, Tuple[int, Optional[float]]] = {}
        self.hits = 0
        self.misses = 0

    def _is_expired(self, expiry: Optional[float]) -> bool:
        if expiry is None:
            return False
        return time.time() > expiry

    def get(self, key: str) -> Optional[str]:
        item = self._store.get(key)
        if not item:
            self.misses += 1
            return None
        val, exp = item
        if self._is_expired(exp):
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        return val

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        exp = time.time() + ex if ex else None
        self._store[key] = (value, exp)
        return True

    def setex(self, key: str, time_sec: int, value: str) -> bool:
        return self.set(key, value, ex=time_sec)

    def delete(self, *keys: str) -> int:
        count = 0
        for k in keys:
            if k in self._store:
                del self._store[k]
                count += 1
            if k in self._lists:
                del self._lists[k]
                count += 1
            if k in self._counters:
                del self._counters[k]
                count += 1
        return count

    def lpush(self, key: str, *values: str) -> int:
        if key not in self._lists:
            self._lists[key] = []
        for v in values:
            self._lists[key].insert(0, v)
        return len(self._lists[key])

    def lrange(self, key: str, start: int, stop: int) -> List[str]:
        lst = self._lists.get(key, [])
        if stop == -1:
            return lst[start:]
        return lst[start:stop + 1]

    def ltrim(self, key: str, start: int, stop: int) -> bool:
        if key in self._lists:
            if stop == -1:
                self._lists[key] = self._lists[key][start:]
            else:
                self._lists[key] = self._lists[key][start:stop + 1]
        return True

    def incr(self, key: str) -> int:
        val, exp = self._counters.get(key, (0, None))
        if self._is_expired(exp):
            val = 0
            exp = None
        val += 1
        self._counters[key] = (val, exp)
        return val

    def expire(self, key: str, time_sec: int) -> bool:
        exp = time.time() + time_sec
        if key in self._store:
            val, _ = self._store[key]
            self._store[key] = (val, exp)
            return True
        if key in self._counters:
            val, _ = self._counters[key]
            self._counters[key] = (val, exp)
            return True
        return False

    def keys(self, pattern: str = "*") -> List[str]:
        now = time.time()
        active = [k for k, (_, exp) in self._store.items() if exp is None or exp > now]
        active.extend(self._lists.keys())
        active.extend([k for k, (_, exp) in self._counters.items() if exp is None or exp > now])
        return list(set(active))

    def ping(self) -> bool:
        return True


class RedisService:
    _client = None
    _is_live_redis = False
    _fallback = None
    _hits = 0
    _misses = 0

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                import redis
                client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1.5)
                client.ping()
                cls._client = client
                cls._is_live_redis = True
                log.info(f"Connected to live Redis at {REDIS_URL}")
            except Exception as e:
                log.info(f"Redis daemon not reachable at {REDIS_URL} ({e}). Initializing embedded high-performance Redis cache store.")
                cls._fallback = InMemoryRedisFallback()
                cls._client = cls._fallback
                cls._is_live_redis = False
        return cls._client

    @classmethod
    def set_json(cls, key: str, value: Any, ex: Optional[int] = None, ttl: Optional[int] = None) -> bool:
        try:
            client = cls.get_client()
            serialized = json.dumps(value)
            expiry = ttl or ex
            if expiry:
                client.setex(key, expiry, serialized)
            else:
                client.set(key, serialized)
            return True
        except Exception as e:
            log.warning(f"Redis set_json error on key {key}: {e}")
            return False

    @classmethod
    def get_json(cls, key: str) -> Optional[Any]:
        try:
            client = cls.get_client()
            raw = client.get(key)
            if raw:
                cls._hits += 1
                return json.loads(raw)
            cls._misses += 1
            return None
        except Exception as e:
            log.warning(f"Redis get_json error on key {key}: {e}")
            cls._misses += 1
            return None

    # --- Domain Specific Caching Helpers ---

    @classmethod
    def cache_quote(cls, ticker: str, quote_data: dict, ttl: int = 60) -> bool:
        """Caches live ticker quote for 60 seconds."""
        key = f"market:quote:{ticker.upper()}"
        return cls.set_json(key, quote_data, ex=ttl)

    @classmethod
    def get_cached_quote(cls, ticker: str) -> Optional[dict]:
        key = f"market:quote:{ticker.upper()}"
        return cls.get_json(key)

    @classmethod
    def cache_fundamentals(cls, ticker: str, data: dict, ttl: int = 3600) -> bool:
        """Caches fundamental metrics for 1 hour."""
        key = f"market:fundamentals:{ticker.upper()}"
        return cls.set_json(key, data, ex=ttl)

    @classmethod
    def get_cached_fundamentals(cls, ticker: str) -> Optional[dict]:
        key = f"market:fundamentals:{ticker.upper()}"
        return cls.get_json(key)

    @classmethod
    def cache_filings(cls, ticker: str, filings: list, ttl: int = 1800) -> bool:
        """Caches official SEC EDGAR filings for 30 minutes."""
        key = f"sec:filings:{ticker.upper()}"
        return cls.set_json(key, filings, ex=ttl)

    @classmethod
    def get_cached_filings(cls, ticker: str) -> Optional[list]:
        key = f"sec:filings:{ticker.upper()}"
        return cls.get_json(key)

    @classmethod
    def push_chat_turn(cls, user_id: int, role: str, content: str, max_turns: int = 30) -> None:
        """Pushes chat message to Redis list for ultra-fast multi-turn conversation retrieval."""
        try:
            client = cls.get_client()
            key = f"session:{user_id}:history"
            payload = json.dumps({"role": role, "content": content, "timestamp": time.time()})
            client.lpush(key, payload)
            client.ltrim(key, 0, max_turns - 1)
            client.expire(key, 86400 * 7) # 7 days session retention
        except Exception as e:
            log.warning(f"Redis push_chat_turn error: {e}")

    @classmethod
    def get_cached_chat_history(cls, user_id: int, limit: int = 15) -> List[Dict[str, str]]:
        """Retrieves cached conversational session history in chronological order."""
        try:
            client = cls.get_client()
            key = f"session:{user_id}:history"
            raw_turns = client.lrange(key, 0, limit - 1)
            result = []
            for r in reversed(raw_turns):
                try:
                    result.append(json.loads(r))
                except Exception:
                    pass
            return result
        except Exception as e:
            log.warning(f"Redis get_cached_chat_history error: {e}")
            return []

    @classmethod
    def check_rate_limit(cls, user_id: int, limit: int = 25, window_sec: int = 60) -> Tuple[bool, int]:
        """Redis-powered atomic fixed-window rate limiter."""
        try:
            client = cls.get_client()
            current_window = int(time.time() // window_sec)
            key = f"ratelimit:{user_id}:{current_window}"
            count = client.incr(key)
            if count == 1:
                client.expire(key, window_sec + 5)
            allowed = count <= limit
            return allowed, count
        except Exception as e:
            log.warning(f"Redis rate limit error: {e}")
            return True, 1

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Returns Redis health, caching performance, and key count."""
        try:
            client = cls.get_client()
            keys = client.keys("*")
            is_live = cls._is_live_redis
            return {
                "status": "connected",
                "engine": "Redis Daemon" if is_live else "Embedded Redis Cache Store",
                "is_live_server": is_live,
                "url": REDIS_URL if is_live else "in-memory-redis",
                "cached_keys_count": len(keys),
                "keys_sample": keys[:10],
                "cache_hits": cls._hits + (cls._fallback.hits if cls._fallback else 0),
                "cache_misses": cls._misses + (cls._fallback.misses if cls._fallback else 0)
            }
        except Exception as e:
            return {
                "status": "error",
                "engine": "Unknown",
                "error": str(e)
            }

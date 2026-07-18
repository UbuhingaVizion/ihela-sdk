import threading
import time


class RateLimiter:
    """Token bucket rate limiter for client-side throttling.

    Default: 100 requests per minute per instance.
    """

    def __init__(self, max_requests: int = 100, period_seconds: float = 60.0):
        self._max_requests = max_requests
        self._period = period_seconds
        self._tokens = float(max_requests)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        new_tokens = elapsed * (self._max_requests / self._period)
        self._tokens = min(float(self._max_requests), self._tokens + new_tokens)
        self._last_refill = now

    def acquire(self) -> bool:
        """Try to acquire a token. Returns True if allowed, False if rate limited."""
        with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            return False

    @property
    def available_tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens

    def reset(self) -> None:
        with self._lock:
            self._tokens = float(self._max_requests)
            self._last_refill = time.monotonic()

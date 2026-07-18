import threading
import time
from typing import Any

from .exceptions import iHelaCircuitOpenError


class CircuitBreaker:
    """Prevents cascading failures by opening the circuit after consecutive errors.

    States:
    - Closed: normal operation, calls pass through
    - Open: calls immediately raise iHelaCircuitOpenError
    - Half-open: first call after cooldown probes the service
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        cooldown_seconds: float = 30.0,
    ):
        self._failure_threshold = failure_threshold
        self._cooldown_seconds = cooldown_seconds
        self._failure_count = 0
        self._last_failure_time: float = 0.0
        self._state: str = "closed"
        self._lock = threading.Lock()

    @property
    def is_open(self) -> bool:
        return self._state == "open"

    @property
    def state(self) -> str:
        return self._state

    @property
    def failure_count(self) -> int:
        return self._failure_count

    def _transition_to_half_open(self) -> None:
        self._state = "half_open"

    def call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        with self._lock:
            if self._state == "open":
                if time.time() - self._last_failure_time >= self._cooldown_seconds:
                    self._transition_to_half_open()
                else:
                    raise iHelaCircuitOpenError(
                        "Circuit breaker is open. "
                        "Too many consecutive failures. Try again later."
                    )

        try:
            result = func(*args, **kwargs)
            with self._lock:
                self._failure_count = 0
                self._state = "closed"
            return result
        except Exception:
            with self._lock:
                self._failure_count += 1
                self._last_failure_time = time.time()
                if self._failure_count >= self._failure_threshold:
                    self._state = "open"
            raise

    def reset(self) -> None:
        with self._lock:
            self._failure_count = 0
            self._state = "closed"
            self._last_failure_time = 0.0

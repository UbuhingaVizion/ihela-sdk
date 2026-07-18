import logging
import uuid
from typing import Any

import httpx

from .circuit_breaker import CircuitBreaker
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

_UA = "ihela-sdk/0.3.0 (python)"


class BaseClient:
    """Shared base for all iHela clients.

    Provides:
    - Connection pooling via httpx.Client reuse
    - User-Agent header
    - Rate limiter (optional)
    - Circuit breaker (optional)
    - Environment guard for production warnings
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        prod: bool = False,
        ihela_base_url: str = "",
        ssl_cert: Any | None = None,
        signature_key: str | None = None,
        rate_limit: int = 0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_cooldown: float = 30.0,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.prod_env = prod
        self.ssl_cert = ssl_cert
        self.signature_key = signature_key
        self.auth_token_object: dict[str, Any] | None = None
        self.ihela_base_url = ihela_base_url

        # Connection pooling: one Client per instance
        self._http: httpx.Client | None = None

        # Guardrails
        self._rate_limiter = (
            RateLimiter(max_requests=rate_limit) if rate_limit > 0 else None
        )
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            cooldown_seconds=circuit_breaker_cooldown,
        )

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        return self._circuit_breaker

    @property
    def rate_limiter(self) -> RateLimiter | None:
        return self._rate_limiter

    def _check_rate_limit(self) -> None:
        if self._rate_limiter is None:
            return
        if not self._rate_limiter.acquire():
            from .exceptions import iHelaRateLimitError

            raise iHelaRateLimitError(
                "Rate limit exceeded. Too many requests in a short period."
            )

    def _get_http(self) -> httpx.Client:
        if self._http is None:
            self._http = httpx.Client(
                cert=self.ssl_cert,
                timeout=httpx.Timeout(15.0),
                headers={"User-Agent": _UA},
            )
        return self._http

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        self._check_rate_limit()

        def _call() -> httpx.Response:
            http = self._get_http()
            return http.request(method, url, **kwargs)  # type: ignore[no-any-return]

        result: Any = self._circuit_breaker.call(_call)
        return result  # type: ignore[no-any-return]

    def _generate_reference(self) -> str:
        return str(uuid.uuid4())

    def close(self) -> None:
        if self._http is not None:
            self._http.close()
            self._http = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f"<{self.__class__.__name__} prod_env={self.prod_env}>"

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import httpx

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 0.5,
    max_backoff: float = 8.0,
    retry_on_exceptions: tuple[type[BaseException], ...] = (
        httpx.ConnectError,
        httpx.ReadTimeout,
        httpx.WriteTimeout,
        httpx.PoolTimeout,
    ),
    retry_on_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that retries HTTP calls with exponential backoff.

    Retries on:
    - Connection errors, read/write/pool timeouts
    - HTTP status codes 429 (rate limited) and 5xx (server errors)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: BaseException | None = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        raise
                    delay = min(backoff_factor * (2**attempt), max_backoff)
                    time.sleep(delay)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in retry_on_status_codes:
                        last_exception = e
                        if attempt == max_retries:
                            raise
                        delay = min(backoff_factor * (2**attempt), max_backoff)
                        time.sleep(delay)
                    else:
                        raise
            raise last_exception  # type: ignore[misc]

        return wrapper

    return decorator

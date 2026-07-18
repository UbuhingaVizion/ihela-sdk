from typing import Any


class iHelaError(Exception):
    """Base exception for all iHela SDK errors."""


class iHelaAuthenticationError(iHelaError):
    """Raised when client credentials or token authentication fail."""


class iHelaAPIError(iHelaError):
    """Raised when the iHela gateway returns an error response.

    The message is intentionally generic to prevent information leakage.
    Use ``response_code`` and ``status_code`` for programmatic handling
    (logging, retry logic, monitoring). Never expose these to end users.

    Attributes:
        status_code: HTTP status code of the response.
        response_code: iHela response code (``"00"`` success, ``"05"``
            insufficient funds, etc.). For developers only.
        is_retryable: ``True`` for transient failures (5xx, code ``"07"``)
            that may succeed on retry.
    """

    def __init__(
        self,
        message: str = "An error occurred while communicating with the iHela gateway.",
        status_code: int | None = None,
        response_code: str | None = None,
        response_data: Any = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_code = response_code
        self._response_data = response_data

    @property
    def is_retryable(self) -> bool:
        """``True`` for transient failures that may succeed on retry."""
        if self.status_code is not None and self.status_code >= 500:
            return True
        if self.response_code == "07":
            return True
        return False


class iHelaCircuitOpenError(iHelaError):
    """Raised when the circuit breaker is open (client-side). All calls
    are suspended until the cooldown period expires."""


class iHelaRateLimitError(iHelaError):
    """Raised when the client-side rate limiter has been exceeded."""

from unittest.mock import MagicMock

import pytest

from ihela_sdk.core.circuit_breaker import CircuitBreaker
from ihela_sdk.core.exceptions import (
    iHelaAPIError,
    iHelaCircuitOpenError,
)
from ihela_sdk.core.rate_limiter import RateLimiter
from ihela_sdk.core.validators import validate_response


class TestCircuitBreaker:
    def test_closed_by_default(self):
        cb = CircuitBreaker()
        assert cb.state == "closed"
        assert not cb.is_open

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2)
        failing = MagicMock(side_effect=ValueError("fail"))
        with pytest.raises(ValueError):
            cb.call(failing)
        with pytest.raises(ValueError):
            cb.call(failing)
        assert cb.is_open

    def test_raises_circuit_open(self):
        cb = CircuitBreaker(failure_threshold=1, cooldown_seconds=60)
        with pytest.raises(ValueError):
            cb.call(MagicMock(side_effect=ValueError("fail")))
        with pytest.raises(iHelaCircuitOpenError):
            cb.call(MagicMock())

    def test_reset_clears_state(self):
        cb = CircuitBreaker(failure_threshold=1)
        with pytest.raises(ValueError):
            cb.call(MagicMock(side_effect=ValueError("fail")))
        assert cb.is_open
        cb.reset()
        assert cb.state == "closed"

    def test_success_resets(self):
        cb = CircuitBreaker(failure_threshold=2)
        with pytest.raises(ValueError):
            cb.call(MagicMock(side_effect=ValueError("fail")))
        assert cb.failure_count == 1
        cb.call(MagicMock(return_value=True))
        assert cb.failure_count == 0
        assert cb.state == "closed"


class TestRateLimiter:
    def test_acquire_returns_true_initially(self):
        rl = RateLimiter(max_requests=100)
        assert rl.acquire() is True

    def test_acquire_returns_false_when_exhausted(self):
        rl = RateLimiter(max_requests=1, period_seconds=60)
        assert rl.acquire() is True
        assert rl.acquire() is False


class TestValidators:
    def test_passes_on_success(self):
        data = {"success": True, "response_code": "00", "response_status": 200}
        assert validate_response(data) == data

    def test_raises_on_error_code(self):
        with pytest.raises(iHelaAPIError) as exc:
            validate_response({"response_code": "05", "response_status": 200})
        assert exc.value.response_code == "05"

    def test_raises_on_http_error(self):
        with pytest.raises(iHelaAPIError) as exc:
            validate_response({"response_status": 500})
        assert exc.value.status_code == 500

    def test_is_retryable(self):
        e1 = iHelaAPIError(status_code=500)
        assert e1.is_retryable is True
        e2 = iHelaAPIError(response_code="07")
        assert e2.is_retryable is True
        e3 = iHelaAPIError(status_code=400)
        assert e3.is_retryable is False
        e4 = iHelaAPIError(response_code="05")
        assert e4.is_retryable is False

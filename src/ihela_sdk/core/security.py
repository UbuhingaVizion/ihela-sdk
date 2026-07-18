import hashlib
import hmac
from typing import Any

from pydantic import BaseModel, Field

_SENSITIVE_KEYS: set[str] = {
    "pin_code",
    "access_token",
    "refresh_token",
    "client_secret",
    "client_id",
    "password",
    "token",
    "secret",
    "api_key",
    "authorization",
}


def mask_sensitive_data(data: Any) -> Any:
    if isinstance(data, dict):
        masked: dict[str, Any] = {}
        for k, v in data.items():
            if k in _SENSITIVE_KEYS:
                masked[k] = "********"
            else:
                masked[k] = mask_sensitive_data(v)
        return masked
    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data


def generate_signature(payload: str, secret_key: str) -> str:
    return hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_signature(payload: str, signature: str, secret_key: str) -> bool:
    expected = generate_signature(payload, secret_key)
    return hmac.compare_digest(expected, signature)


class DepositPayload(BaseModel):
    credit_account: str = Field(
        ..., min_length=3, max_length=50, pattern=r"^[A-Z0-9\-]+$"
    )
    credit_account_holder: str = Field(..., min_length=2, max_length=100)
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=255)
    external_reference: str = Field(..., min_length=3, max_length=100)
    pin_code: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$")
    external_code: str = Field("", max_length=100)


class WithdrawalPayload(BaseModel):
    debit_account: str = Field(
        ..., min_length=3, max_length=50, pattern=r"^[A-Z0-9\-]+$"
    )
    debit_account_holder: str = Field(..., min_length=2, max_length=100)
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=255)
    external_reference: str = Field(..., min_length=3, max_length=100)
    pin_code: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$")


class ValidateWithdrawalPayload(BaseModel):
    external_reference: str = Field(..., min_length=3, max_length=100)
    pin_code: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$")
    agent_code: str = Field(..., min_length=3, max_length=50)
    amount: str = Field(..., min_length=1)
    external_code: str = Field("", max_length=100)
    validation_operation_code: str = Field(..., min_length=3)

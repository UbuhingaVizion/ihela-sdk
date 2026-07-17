import hashlib
import hmac
from typing import Any

from pydantic import BaseModel, Field


def mask_sensitive_data(data: Any) -> Any:
    """Mask sensitive fields (pins, credentials, tokens) inside logging payloads."""
    if isinstance(data, dict):
        masked = {}
        for k, v in data.items():
            if k in {
                "pin_code",
                "access_token",
                "client_secret",
                "refresh_token",
                "client_id",
            }:
                masked[k] = "********"
            else:
                masked[k] = mask_sensitive_data(v)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data


def generate_signature(payload: str, secret_key: str) -> str:
    """Generate a cryptographic HMAC-SHA256 signature for payload verification."""
    return hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class DepositPayload(BaseModel):
    """Pydantic schema to validate deposits before gateway dispatch."""

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
    """Pydantic schema to validate withdrawals before gateway dispatch."""

    debit_account: str = Field(
        ..., min_length=3, max_length=50, pattern=r"^[A-Z0-9\-]+$"
    )
    debit_account_holder: str = Field(..., min_length=2, max_length=100)
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=255)
    external_reference: str = Field(..., min_length=3, max_length=100)
    pin_code: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$")


class ValidateWithdrawalPayload(BaseModel):
    """Pydantic schema to validate withdrawal validations before gateway dispatch."""

    external_reference: str = Field(..., min_length=3, max_length=100)
    pin_code: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$")
    agent_code: str = Field(..., min_length=3, max_length=50)
    amount: str = Field(..., min_length=1)
    external_code: str = Field("", max_length=100)
    validation_operation_code: str = Field(..., min_length=3)

import pytest
from pydantic import ValidationError

from ihela_client.security import (
    DepositPayload,
    WithdrawalPayload,
    generate_signature,
    mask_sensitive_data,
)


def test_generate_signature():
    payload = '{"amount": 1000, "credit_account": "ACT123"}'
    key = "super_secret_signing_key"
    sig = generate_signature(payload, key)
    # The signature should be a valid SHA-256 hex string (64 characters)
    assert len(sig) == 64
    # Re-generating with same inputs should be deterministic
    assert sig == generate_signature(payload, key)


def test_mask_sensitive_data():
    sensitive_payload = {
        "account_number": "123456",
        "pin_code": "1234",
        "access_token": "secret_jwt_token",
        "nested": {
            "client_secret": "my_secret",
            "non_sensitive": "ok",
        },
    }
    masked = mask_sensitive_data(sensitive_payload)
    assert masked["account_number"] == "123456"
    assert masked["pin_code"] == "********"
    assert masked["access_token"] == "********"
    assert masked["nested"]["client_secret"] == "********"
    assert masked["nested"]["non_sensitive"] == "ok"


def test_deposit_payload_validation():
    # Valid payload
    payload = DepositPayload(
        credit_account="ACT-1234",
        credit_account_holder="John Doe",
        amount=1500.50,
        description="Invoice Payment",
        external_reference="REF-883",
        pin_code="1234",
        external_code="EXT-11",
    )
    assert payload.amount == 1500.50

    # Invalid amount (must be > 0)
    with pytest.raises(ValidationError):
        DepositPayload(
            credit_account="ACT-1234",
            credit_account_holder="John Doe",
            amount=-10.0,
            description="Invoice Payment",
            external_reference="REF-883",
            pin_code="1234",
        )

    # Invalid PIN (must be numeric)
    with pytest.raises(ValidationError):
        DepositPayload(
            credit_account="ACT-1234",
            credit_account_holder="John Doe",
            amount=100.0,
            description="Invoice Payment",
            external_reference="REF-883",
            pin_code="ABCD",
        )


def test_withdrawal_payload_validation():
    # Valid payload
    payload = WithdrawalPayload(
        debit_account="ACT-5678",
        debit_account_holder="Jane Doe",
        amount=200.0,
        description="Cash withdrawal",
        external_reference="REF-992",
        pin_code="9876",
    )
    assert payload.pin_code == "9876"

    # Invalid debit account format (regex check)
    with pytest.raises(ValidationError):
        WithdrawalPayload(
            debit_account="invalid_account_#",
            debit_account_holder="Jane Doe",
            amount=200.0,
            description="Cash withdrawal",
            external_reference="REF-992",
            pin_code="9876",
        )

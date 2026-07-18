import pytest
from pydantic import ValidationError

from ihela_sdk import (
    DepositPayload,
    WithdrawalPayload,
    generate_signature,
    mask_sensitive_data,
)


def test_generate_signature():
    payload = '{"amount": 1000, "credit_account": "ACT123"}'
    sig = generate_signature(payload, "super_secret_signing_key")
    assert len(sig) == 64
    assert sig == generate_signature(payload, "super_secret_signing_key")


def test_mask_sensitive_data():
    sensitive = {
        "account_number": "123456",
        "pin_code": "1234",
        "access_token": "secret_token",
        "nested": {"client_secret": "my_secret", "non_sensitive": "ok"},
    }
    masked = mask_sensitive_data(sensitive)
    assert masked["account_number"] == "123456"
    assert masked["pin_code"] == "********"
    assert masked["access_token"] == "********"
    assert masked["nested"]["client_secret"] == "********"
    assert masked["nested"]["non_sensitive"] == "ok"


def test_deposit_payload_validation():
    payload = DepositPayload(
        credit_account="ACT-1234",
        credit_account_holder="John Doe",
        amount=1500.50,
        description="Invoice",
        external_reference="REF-883",
        pin_code="1234",
        external_code="EXT-11",
    )
    assert payload.amount == 1500.50
    with pytest.raises(ValidationError):
        DepositPayload(
            credit_account="ACT-1234",
            credit_account_holder="John Doe",
            amount=-10.0,
            description="Invoice",
            external_reference="REF-883",
            pin_code="1234",
        )
    with pytest.raises(ValidationError):
        DepositPayload(
            credit_account="ACT-1234",
            credit_account_holder="John Doe",
            amount=100.0,
            description="Invoice",
            external_reference="REF-883",
            pin_code="ABCD",
        )


def test_withdrawal_payload_validation():
    payload = WithdrawalPayload(
        debit_account="ACT-5678",
        debit_account_holder="Jane Doe",
        amount=200.0,
        description="Cash",
        external_reference="REF-992",
        pin_code="9876",
    )
    assert payload.pin_code == "9876"
    with pytest.raises(ValidationError):
        WithdrawalPayload(
            debit_account="invalid#",
            debit_account_holder="Jane Doe",
            amount=200.0,
            description="Cash",
            external_reference="REF-992",
            pin_code="9876",
        )

from unittest.mock import MagicMock, patch

from ihela_sdk import MerchantClient


@patch("ihela_sdk.merchant_client.httpx.Client.post")
def test_merchant_client_init(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"access_token": "test_token", "token_type": "Bearer"}
    mock_post.return_value = mock_resp

    client = MerchantClient("client_id", "client_secret")
    assert client.is_authenticated() is True
    assert client.get_access_token() == "test_token"
    assert client.get_auth_headers() == {"Authorization": "Bearer test_token"}


@patch("ihela_sdk.merchant_client.httpx.Client.post")
def test_init_bill(mock_post):
    mock_auth_resp = MagicMock()
    mock_auth_resp.status_code = 200
    mock_auth_resp.json.return_value = {
        "access_token": "test_token",
        "token_type": "Bearer",
    }

    mock_bill_resp = MagicMock()
    mock_bill_resp.status_code = 200
    mock_bill_resp.json.return_value = {
        "bill": {"code": "BILL-1234", "merchant_reference": "ref-1234"},
        "response_status": 200,
    }

    mock_post.side_effect = [mock_auth_resp, mock_bill_resp]

    client = MerchantClient("client_id", "client_secret")
    bill = client.init_bill(
        amount=2000,
        user="user_id",
        description="description",
        reference="ref-1234",
        pin_code="1234",
    )
    assert bill["response_status"] == 200
    assert bill["bill"]["code"] == "BILL-1234"

    call_kwargs = mock_post.call_args_list[1][1]
    assert "json" in call_kwargs
    assert call_kwargs["json"]["debit_account"] == "user_id"
    assert call_kwargs["json"]["merchant_reference"] == "ref-1234"
    assert call_kwargs["json"]["pin_code"] == "1234"


@patch("ihela_sdk.merchant_client.httpx.Client.post")
def test_verify_bill(mock_post):
    mock_auth_resp = MagicMock()
    mock_auth_resp.status_code = 200
    mock_auth_resp.json.return_value = {
        "access_token": "test_token",
        "token_type": "Bearer",
    }

    mock_verify_resp = MagicMock()
    mock_verify_resp.status_code = 200
    mock_verify_resp.json.return_value = {
        "response_code": "00",
        "response_data": {
            "bill_code": "CODE-1234",
            "merchant_reference": "ref-1234",
            "payment_reference": None,
            "status": "Paid",
        },
        "success": True,
    }

    mock_post.side_effect = [mock_auth_resp, mock_verify_resp]

    client = MerchantClient("client_id", "client_secret")
    result = client.verify_bill("CODE-1234", "ref-1234", "1234")
    assert result["success"] is True
    assert result["response_data"]["status"] == "Paid"

    call_kwargs = mock_post.call_args_list[1][1]
    assert "json" in call_kwargs
    assert call_kwargs["json"]["bill_code"] == "CODE-1234"
    assert call_kwargs["json"]["merchant_reference"] == "ref-1234"
    assert call_kwargs["json"]["pin_code"] == "1234"


@patch("ihela_sdk.merchant_client.httpx.Client.post")
def test_cashin_client(mock_post):
    mock_auth_resp = MagicMock()
    mock_auth_resp.status_code = 200
    mock_auth_resp.json.return_value = {
        "access_token": "test_token",
        "token_type": "Bearer",
    }

    mock_cashin_resp = MagicMock()
    mock_cashin_resp.status_code = 200
    mock_cashin_resp.json.return_value = {
        "response_code": "00",
        "response_data": {"reference": "REF-5678"},
        "success": True,
    }

    mock_post.side_effect = [mock_auth_resp, mock_cashin_resp]

    client = MerchantClient("client_id", "client_secret")
    result = client.cashin_client(
        bank_slug="MF1-0001",
        account="000016-01",
        amount=20000,
        merchant_reference="REF3223",
        description="Refunding customer",
        pin_code="1234",
    )
    assert result["success"] is True

    call_kwargs = mock_post.call_args_list[1][1]
    assert "json" in call_kwargs
    assert call_kwargs["json"]["credit_bank"] == "MF1-0001"
    assert call_kwargs["json"]["credit_account"] == "000016-01"
    assert call_kwargs["json"]["currency"] == "BIF"
    assert call_kwargs["json"]["pin_code"] == "1234"


@patch("ihela_sdk.merchant_client.httpx.Client.get")
@patch("ihela_sdk.merchant_client.httpx.Client.post")
def test_get_bank_list(mock_post, mock_get):
    mock_auth_resp = MagicMock()
    mock_auth_resp.status_code = 200
    mock_auth_resp.json.return_value = {"access_token": "token", "token_type": "Bearer"}
    mock_post.return_value = mock_auth_resp

    mock_banks = MagicMock()
    mock_banks.status_code = 200
    mock_banks.json.return_value = {
        "response_status": 200,
        "banks": [{"name": "Bank1"}, {"name": "Bank2"}],
    }
    mock_get.return_value = mock_banks

    client = MerchantClient("client_id", "client_secret")
    banks = client.get_bank_list()
    assert len(banks["banks"]) == 2


@patch("ihela_sdk.merchant_client.httpx.Client.post")
def test_merchant_client_with_token(mock_post):
    token = {"access_token": "injected_token", "token_type": "Bearer"}

    client = MerchantClient("client_id", "client_secret", token=token)
    assert client.is_authenticated() is True
    assert client.get_access_token() == "injected_token"
    assert client.get_auth_headers() == {"Authorization": "Bearer injected_token"}
    mock_post.assert_not_called()


@patch("ihela_sdk.merchant_client.httpx.Client.post")
def test_merchant_client_no_auto_auth(mock_post):
    client = MerchantClient("client_id", "client_secret", auto_auth=False)
    assert client.is_authenticated() is False
    mock_post.assert_not_called()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"access_token": "lazy_token", "token_type": "Bearer"}
    mock_post.return_value = mock_resp

    assert client.get_auth_headers() == {"Authorization": "Bearer lazy_token"}
    mock_post.assert_called_once()

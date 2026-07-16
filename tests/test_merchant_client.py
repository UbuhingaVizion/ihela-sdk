from unittest.mock import MagicMock, patch

from ihela_client import MerchantClient


@patch("ihela_client.merchant_client.requests.post")
def test_merchant_client_init(mock_post):
    # Mock authentication response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"access_token": "test_token", "token_type": "Bearer"}
    mock_post.return_value = mock_resp

    client = MerchantClient("client_id", "client_secret")
    assert client.is_authenticated() is True
    assert client.get_access_token() == "test_token"
    assert client.get_auth_headers() == {"Authorization": "Bearer test_token"}


@patch("ihela_client.merchant_client.requests.post")
def test_init_bill(mock_post):
    # Mock auth response
    mock_auth_resp = MagicMock()
    mock_auth_resp.status_code = 200
    mock_auth_resp.json.return_value = {
        "access_token": "test_token",
        "token_type": "Bearer",
    }

    # Mock bill init response
    mock_bill_resp = MagicMock()
    mock_bill_resp.status_code = 200
    mock_bill_resp.json.return_value = {
        "bill": {"code": "BILL-1234", "merchant_reference": "ref-1234"},
        "response_status": 200,
    }

    mock_post.side_effect = [mock_auth_resp, mock_bill_resp]

    client = MerchantClient("client_id", "client_secret")
    bill = client.init_bill(2000, "user_id", "description", "ref-1234")
    assert bill["response_status"] == 200
    assert bill["bill"]["code"] == "BILL-1234"

from unittest.mock import MagicMock, patch

from ihela_sdk import MerchantClient


def test_merchant_client_init():
    with patch("ihela_sdk.core.base.BaseClient._request") as mock_req:
        mock_req.return_value = MagicMock(
            status_code=200,
            json=MagicMock(
                return_value={"access_token": "test_token", "token_type": "Bearer"}
            ),
        )
        client = MerchantClient("client_id", "client_secret")
        assert client.is_authenticated() is True
        assert client.get_access_token() == "test_token"


def test_init_bill():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.side_effect = [
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            ),
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={
                        "bill": {"code": "B1", "merchant_reference": "r1"},
                        "response_status": 200,
                    }
                ),
            ),
        ]
        client = MerchantClient("client_id", "client_secret")
        bill = client.init_bill(
            amount=2000, user="u", description="d", reference="r", pin_code="1234"
        )
        assert bill["response_status"] == 200


def test_verify_bill():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.side_effect = [
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            ),
            MagicMock(
                status_code=200,
                json=MagicMock(return_value={"success": True, "response_status": 200}),
            ),
        ]
        client = MerchantClient("client_id", "client_secret")
        result = client.verify_bill("C-1234", "r-1234", "1234")
        assert result["success"] is True


def test_cashin_client():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.side_effect = [
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            ),
            MagicMock(
                status_code=200,
                json=MagicMock(return_value={"success": True, "response_status": 200}),
            ),
        ]
        client = MerchantClient("client_id", "client_secret")
        result = client.cashin_client(
            "MF1-0001", "000016-01", 20000, "R3223", "desc", pin_code="1234"
        )
        assert result["success"] is True


def test_get_bank_list():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.side_effect = [
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            ),
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"response_status": 200, "banks": [{"name": "B1"}]}
                ),
            ),
        ]
        client = MerchantClient("client_id", "client_secret")
        banks = client.get_bank_list()
        assert len(banks["banks"]) == 1


def test_merchant_client_with_token():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        client = MerchantClient(
            "client_id",
            "client_secret",
            token={"access_token": "i", "token_type": "Bearer"},
        )
        assert client.is_authenticated() is True
        assert client.get_access_token() == "i"
        mr.assert_not_called()


def test_merchant_client_no_auto_auth():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        client = MerchantClient("client_id", "client_secret", auto_auth=False)
        assert client.is_authenticated() is False
        mr.assert_not_called()
        mr.return_value = MagicMock(
            status_code=200,
            json=MagicMock(
                return_value={"access_token": "lazy_token", "token_type": "Bearer"}
            ),
        )
        assert client.get_auth_headers() == {"Authorization": "Bearer lazy_token"}
        mr.assert_called_once()

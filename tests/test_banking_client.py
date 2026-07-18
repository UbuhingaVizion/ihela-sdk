import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ihela_sdk import AsyncBankingClient, BankingClient


def test_banking_client_ping():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.side_effect = [
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            ),
            MagicMock(status_code=200, json=MagicMock(return_value={"success": True})),
        ]
        client = BankingClient("id", "secret")
        res = client.ping()
        assert res["success"] is True


def test_banking_client_withdrawal():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.side_effect = [
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            ),
            MagicMock(status_code=200, json=MagicMock(return_value={"success": True})),
        ]
        client = BankingClient("id", "secret")
        res = client.withdrawal(
            "DEBIT-1234", "holder", 1000.0, "desc", "REF-123", "1234"
        )
        assert res["success"] is True


def test_banking_client_deposit():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.side_effect = [
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            ),
            MagicMock(status_code=200, json=MagicMock(return_value={"success": True})),
        ]
        client = BankingClient("id", "secret")
        res = client.deposit("ACT-123", "holder", 500.0, "desc", "REF-123", "1234")
        assert res["success"] is True


def test_banking_client_request_token():
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
                json=MagicMock(return_value={"access": "new", "refresh": "new_ref"}),
            ),
        ]
        client = BankingClient("id", "secret")
        res = client.request_token("user", "pass")
        assert res["access"] == "new"


def test_banking_client_transaction_fee():
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
                    return_value={"success": True, "response_data": {"fee": "100"}}
                ),
            ),
        ]
        client = BankingClient("id", "secret")
        res = client.transaction_fee("BIF", "withdrawal", "4000")
        assert res["response_data"]["fee"] == "100"


def test_banking_client_account_lookup():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.side_effect = [
            MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            ),
            MagicMock(status_code=200, json=MagicMock(return_value={"success": True})),
        ]
        client = BankingClient("id", "secret")
        res = client.account_lookup("76077736")
        assert res["success"] is True


def test_banking_client_with_token():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        client = BankingClient(
            "id", "secret", token={"access_token": "i", "token_type": "Bearer"}
        )
        assert client.is_authenticated() is True
        mr.assert_not_called()


def test_banking_client_no_auto_auth():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        client = BankingClient("id", "secret", auto_auth=False)
        assert client.is_authenticated() is False
        mr.assert_not_called()
        mr.return_value = MagicMock(
            status_code=200,
            json=MagicMock(
                return_value={"access_token": "token", "token_type": "Bearer"}
            ),
        )
        assert client.get_auth_headers() == {"Authorization": "Bearer token"}
        mr.assert_called_once()


def test_async_banking_client_ping():
    async def run_test():
        mock_auth = MagicMock()
        mock_auth.status_code = 200
        mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mp:
            mp.return_value = mock_auth
            c = AsyncBankingClient("id", "secret")
            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mg:
                mg.return_value = MagicMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                )
                res = await c.ping()
                assert res["success"] is True

    asyncio.run(run_test())


def test_async_banking_client_with_token():
    async def run_test():
        c = AsyncBankingClient(
            "id", "secret", token={"access_token": "i", "token_type": "Bearer"}
        )
        assert c.is_authenticated() is True

    asyncio.run(run_test())

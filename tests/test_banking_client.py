import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ihela_client import AsyncBankingClient, BankingClient


@patch("requests.post")
def test_banking_client_ping(mock_post):
    # Mock auth response
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}
    mock_post.return_value = mock_auth

    client = BankingClient("id", "secret")

    with patch("requests.get") as mock_get:
        mock_ping = MagicMock()
        mock_ping.status_code = 200
        mock_ping.json.return_value = {"success": True}
        mock_get.return_value = mock_ping

        res = client.ping()
        assert res["success"] is True


@patch("requests.post")
def test_banking_client_withdrawal(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}

    mock_withdrawal = MagicMock()
    mock_withdrawal.status_code = 200
    mock_withdrawal.json.return_value = {"success": True, "response_message": "Success"}

    mock_post.side_effect = [mock_auth, mock_withdrawal]

    client = BankingClient("id", "secret")
    res = client.withdrawal("debit", "holder", 1000.0, "desc", "ref", "pin")
    assert res["success"] is True


def test_async_banking_client_ping():
    async def run_test():
        mock_auth = MagicMock()
        mock_auth.status_code = 200
        mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_auth
            client = AsyncBankingClient("id", "secret")

            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
                mock_ping = MagicMock()
                mock_ping.status_code = 200
                mock_ping.json.return_value = {"success": True}
                mock_get.return_value = mock_ping

                res = await client.ping()
                assert res["success"] is True

    asyncio.run(run_test())

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ihela_sdk import AsyncBankingClient, BankingClient


@patch("ihela_sdk.banking_client.httpx.Client.post")
def test_banking_client_ping(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}
    mock_post.return_value = mock_auth

    client = BankingClient("id", "secret")

    with patch("ihela_sdk.banking_client.httpx.Client.get") as mock_get:
        mock_ping = MagicMock()
        mock_ping.status_code = 200
        mock_ping.json.return_value = {"success": True}
        mock_get.return_value = mock_ping

        res = client.ping()
        assert res["success"] is True


@patch("ihela_sdk.banking_client.httpx.Client.post")
def test_banking_client_withdrawal(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}

    mock_withdrawal = MagicMock()
    mock_withdrawal.status_code = 200
    mock_withdrawal.json.return_value = {"success": True, "response_message": "Success"}

    mock_post.side_effect = [mock_auth, mock_withdrawal]

    client = BankingClient("id", "secret")
    res = client.withdrawal("DEBIT-1234", "holder", 1000.0, "desc", "REF-123", "1234")
    assert res["success"] is True


@patch("ihela_sdk.banking_client.httpx.Client.post")
def test_banking_client_deposit(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}

    mock_deposit = MagicMock()
    mock_deposit.status_code = 200
    mock_deposit.json.return_value = {
        "success": True,
        "response_message": "Deposit done",
    }

    mock_post.side_effect = [mock_auth, mock_deposit]

    client = BankingClient("id", "secret")
    res = client.deposit("ACT-123", "holder", 500.0, "desc", "REF-123", "1234")
    assert res["success"] is True

    call_kwargs = mock_post.call_args_list[1][1]
    assert "make-deposit/" in call_kwargs.get(
        "url", client.get_url("ihela/api/v1/make-deposit/")
    )


@patch("ihela_sdk.banking_client.httpx.Client.post")
def test_banking_client_request_token(mock_post):
    mock_token = MagicMock()
    mock_token.status_code = 200
    mock_token.json.return_value = {"access": "new_token", "refresh": "new_refresh"}
    mock_post.return_value = mock_token

    client = BankingClient("id", "secret")
    client.auth_token_object = {"access_token": "old", "token_type": "Bearer"}
    res = client.request_token("username", "password")
    assert res["access"] == "new_token"
    assert client.auth_token_object["access"] == "new_token"


@patch("ihela_sdk.banking_client.httpx.Client.post")
def test_banking_client_transaction_fee(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}
    mock_post.return_value = mock_auth

    client = BankingClient("id", "secret")

    mock_fee = MagicMock()
    mock_fee.status_code = 200
    mock_fee.json.return_value = {"success": True, "response_data": {"fee": "100"}}

    with patch(
        "ihela_sdk.banking_client.httpx.Client.post", return_value=mock_fee
    ) as mock_fee_post:
        res = client.transaction_fee("BIF", "withdrawal", "4000")
        assert res["response_data"]["fee"] == "100"

        call_kwargs = mock_fee_post.call_args[1]
        assert call_kwargs["json"]["currency"] == "BIF"
        assert call_kwargs["json"]["operation_type"] == "withdrawal"
        assert call_kwargs["json"]["amount"] == "4000"


@patch("ihela_sdk.banking_client.httpx.Client.post")
def test_banking_client_account_lookup(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}
    mock_post.return_value = mock_auth

    client = BankingClient("id", "secret")

    mock_lookup = MagicMock()
    mock_lookup.status_code = 200
    mock_lookup.json.return_value = {"success": True}

    with patch(
        "ihela_sdk.banking_client.httpx.Client.post", return_value=mock_lookup
    ) as mock_lp:
        res = client.account_lookup("76077736")
        assert res["success"] is True
        assert mock_lp.call_args[1]["json"]["account_number"] == "76077736"


def test_banking_client_with_token():
    token = {"access_token": "injected_token", "token_type": "Bearer"}

    with (
        patch("ihela_sdk.banking_client.httpx.Client.post") as mock_post,
        patch("ihela_sdk.banking_client.httpx.Client.get") as mock_get,
    ):
        mock_ping = MagicMock()
        mock_ping.status_code = 200
        mock_ping.json.return_value = {"success": True}
        mock_get.return_value = mock_ping

        client = BankingClient("id", "secret", token=token)
        assert client.is_authenticated() is True
        res = client.ping()
        assert res["success"] is True
        mock_post.assert_not_called()


def test_banking_client_no_auto_auth():
    with patch("ihela_sdk.banking_client.httpx.Client.post") as mock_post:
        mock_auth = MagicMock()
        mock_auth.status_code = 200
        mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}
        mock_post.return_value = mock_auth

        client = BankingClient("id", "secret", auto_auth=False)
        assert client.is_authenticated() is False
        mock_post.assert_not_called()

        headers = client.get_auth_headers()
        assert headers == {"Authorization": "Bearer token"}
        mock_post.assert_called_once()


def test_async_banking_client_with_token():
    async def run_test():
        token = {"access_token": "injected", "token_type": "Bearer"}
        client = AsyncBankingClient("id", "secret", token=token)
        assert client.is_authenticated() is True
        assert client.auth_token_object is not None
        assert client.auth_token_object["access_token"] == "injected"

    asyncio.run(run_test())


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


def test_async_banking_client_request_token():
    async def run_test():
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"access": "token", "refresh": "refresh"}

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            client = AsyncBankingClient("id", "secret")
            client.auth_token_object = {"access_token": "old", "token_type": "Bearer"}
            res = await client.request_token("user", "pass")
            assert res["access"] == "token"
            assert client.auth_token_object["access"] == "token"

    asyncio.run(run_test())

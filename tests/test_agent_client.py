import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ihela_sdk import AgentClient, AsyncAgentClient


@patch("ihela_sdk.agent_client.httpx.Client.post")
def test_agent_client_ping(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}
    mock_post.return_value = mock_auth

    client = AgentClient("id", "secret")

    with patch("ihela_sdk.agent_client.httpx.Client.get") as mock_get:
        mock_ping = MagicMock()
        mock_ping.status_code = 200
        mock_ping.json.return_value = {"success": True}
        mock_get.return_value = mock_ping

        res = client.ping()
        assert res["success"] is True


@patch("ihela_sdk.agent_client.httpx.Client.post")
def test_agent_client_operations(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}

    mock_op = MagicMock()
    mock_op.status_code = 200
    mock_op.json.return_value = {
        "success": True,
        "validation_operation_code": "val-123",
    }

    mock_post.side_effect = [mock_auth, mock_op]

    client = AgentClient("id", "secret")
    res = client.operation_lookup("op-code", "5000")
    assert res["validation_operation_code"] == "val-123"


@patch("ihela_sdk.agent_client.httpx.Client.post")
def test_agent_client_request_token(mock_post):
    mock_token = MagicMock()
    mock_token.status_code = 200
    mock_token.json.return_value = {"access": "new_token", "refresh": "new_refresh"}
    mock_post.return_value = mock_token

    client = AgentClient("id", "secret")
    client.auth_token_object = {"access_token": "old", "token_type": "Bearer"}
    res = client.request_token("username", "password")
    assert res["access"] == "new_token"
    assert client.auth_token_object["access"] == "new_token"


@patch("ihela_sdk.agent_client.httpx.Client.post")
def test_agent_client_deposit(mock_post):
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

    client = AgentClient("id", "secret")
    res = client.deposit("ACT-123", "holder", 500.0, "desc", "REF-123", "1234")
    assert res["success"] is True


@patch("ihela_sdk.agent_client.httpx.Client.post")
def test_agent_client_validate_withdrawal(mock_post):
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}

    mock_validate = MagicMock()
    mock_validate.status_code = 200
    mock_validate.json.return_value = {"success": True}

    mock_post.side_effect = [mock_auth, mock_validate]

    client = AgentClient("id", "secret")
    res = client.validate_withdrawal(
        "REF-123", "1234", "AGT-001", "5000", "EXT-001", "VAL-001"
    )
    assert res["success"] is True


def test_async_agent_client_ping():
    async def run_test():
        mock_auth = MagicMock()
        mock_auth.status_code = 200
        mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_auth
            client = AsyncAgentClient("id", "secret")

            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
                mock_ping = MagicMock()
                mock_ping.status_code = 200
                mock_ping.json.return_value = {"success": True}
                mock_get.return_value = mock_ping

                res = await client.ping()
                assert res["success"] is True

    asyncio.run(run_test())


def test_async_agent_client_request_token():
    async def run_test():
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"access": "token", "refresh": "refresh"}

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            client = AsyncAgentClient("id", "secret")
            client.auth_token_object = {"access_token": "old", "token_type": "Bearer"}
            res = await client.request_token("user", "pass")
            assert res["access"] == "token"
            assert client.auth_token_object["access"] == "token"

    asyncio.run(run_test())

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ihela_client import AgentClient, AsyncAgentClient


@patch("requests.post")
def test_agent_client_ping(mock_post):
    # Mock auth response
    mock_auth = MagicMock()
    mock_auth.status_code = 200
    mock_auth.json.return_value = {"access_token": "token", "token_type": "Bearer"}
    mock_post.return_value = mock_auth

    client = AgentClient("id", "secret")

    with patch("requests.get") as mock_get:
        mock_ping = MagicMock()
        mock_ping.status_code = 200
        mock_ping.json.return_value = {"success": True}
        mock_get.return_value = mock_ping

        res = client.ping()
        assert res["success"] is True


@patch("requests.post")
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

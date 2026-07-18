import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ihela_sdk import AgentClient, AsyncAgentClient


def test_agent_client_ping():
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
        client = AgentClient("id", "secret")
        res = client.ping()
        assert res["success"] is True


def test_agent_client_operations():
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
                        "success": True,
                        "validation_operation_code": "val-123",
                    }
                ),
            ),
        ]
        client = AgentClient("id", "secret")
        res = client.operation_lookup("op-code", "5000")
        assert res["validation_operation_code"] == "val-123"


def test_agent_client_request_token():
    with patch("ihela_sdk.core.base.BaseClient._request") as mr:
        mr.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"access": "new", "refresh": "new_ref"}),
        )
        client = AgentClient("id", "secret")
        res = client.request_token("user", "pass")
        assert res["access"] == "new"


def test_agent_client_deposit():
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
        client = AgentClient("id", "secret")
        res = client.deposit("ACT-123", "holder", 500.0, "desc", "REF-123", "1234")
        assert res["success"] is True


def test_agent_client_validate_withdrawal():
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
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mp:
            mp.return_value = mock_auth
            c = AsyncAgentClient("id", "secret")
            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mg:
                mg.return_value = MagicMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                )
                res = await c.ping()
                assert res["success"] is True

    asyncio.run(run_test())

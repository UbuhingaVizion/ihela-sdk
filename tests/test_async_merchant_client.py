import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ihela_sdk import AsyncMerchantClient, iHelaAPIError, iHelaAuthenticationError


def test_async_merchant_client_init():
    async def run_test():
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mp:
            mp.return_value = MagicMock(
                status_code=200,
                json=MagicMock(
                    return_value={"access_token": "t", "token_type": "Bearer"}
                ),
            )
            c = AsyncMerchantClient("cid", "csec")
            await c.authenticate()
            assert c.is_authenticated() is True

    asyncio.run(run_test())


def test_async_merchant_client_auth_failure():
    async def run_test():
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mp:
            mp.return_value = MagicMock(status_code=401, text="Unauthorized")
            c = AsyncMerchantClient("cid", "csec")
            with pytest.raises(iHelaAuthenticationError):
                await c.authenticate()

    asyncio.run(run_test())


def test_async_merchant_client_api_failure():
    async def run_test():
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mg:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_resp.text = "Not Found"
            mock_resp.json.side_effect = ValueError("bad json")
            mg.return_value = mock_resp
            c = AsyncMerchantClient("cid", "csec")
            c.auth_token_object = {"access_token": "t", "token_type": "Bearer"}
            with pytest.raises(iHelaAPIError):
                await c.customer_lookup("MF1-0001", "000016-01")

    asyncio.run(run_test())


def test_async_merchant_client_init_bill():
    async def run_test():
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mp:
            mp.side_effect = [
                MagicMock(
                    status_code=200,
                    json=MagicMock(
                        return_value={"access_token": "t", "token_type": "Bearer"}
                    ),
                ),
                MagicMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                ),
            ]
            c = AsyncMerchantClient("cid", "csec")
            await c.authenticate()
            r = await c.init_bill(600, "76000111", "d", "r", pin_code="1234")
            assert r["success"] is True

    asyncio.run(run_test())

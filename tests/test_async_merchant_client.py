import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ihela_client import AsyncMerchantClient, iHelaAPIError, iHelaAuthenticationError


def test_async_merchant_client_init():
    async def run_test():
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "async_test_token",
            "token_type": "Bearer",
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            client = AsyncMerchantClient("client_id", "client_secret")
            await client.authenticate()
            assert client.is_authenticated() is True
            assert client.auth_token_object["access_token"] == "async_test_token"
            headers = await client.get_auth_headers()
            assert headers == {"Authorization": "Bearer async_test_token"}

    asyncio.run(run_test())


def test_async_merchant_client_auth_failure():
    async def run_test():
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized client"

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_resp
            client = AsyncMerchantClient("client_id", "client_secret")
            with pytest.raises(iHelaAuthenticationError):
                await client.authenticate()

    asyncio.run(run_test())


def test_async_merchant_client_api_failure():
    async def run_test():
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Not Found"
        mock_resp.json.side_effect = ValueError("Non JSON response")

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            client = AsyncMerchantClient("client_id", "client_secret")
            client.auth_token_object = {
                "access_token": "test_token",
                "token_type": "Bearer",
            }
            with pytest.raises(iHelaAPIError):
                await client.customer_lookup("MF1-0001", "000016-01")

    asyncio.run(run_test())

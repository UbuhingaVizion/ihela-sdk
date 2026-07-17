import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ihela_sdk import AsyncMerchantClient, iHelaAPIError, iHelaAuthenticationError


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


def test_async_merchant_client_init_bill():
    async def run_test():
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 200
        mock_auth_resp.json.return_value = {
            "access_token": "token",
            "token_type": "Bearer",
        }

        mock_bill_resp = MagicMock()
        mock_bill_resp.status_code = 200
        mock_bill_resp.json.return_value = {
            "response_code": "00",
            "response_data": {"code": "CODE-1234", "reference": None},
            "success": True,
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [mock_auth_resp, mock_bill_resp]
            client = AsyncMerchantClient("client_id", "client_secret")
            await client.authenticate()

            result = await client.init_bill(
                amount=600,
                user="0000000016-01",
                description="Payment merchant",
                reference="752001",
                bank="MF1-0001",
                pin_code="1234",
            )
            assert result["success"] is True
            assert result["response_data"]["code"] == "CODE-1234"

            bill_call = mock_post.call_args_list[1][1]
            assert "json" in bill_call
            assert bill_call["json"]["debit_account"] == "0000000016-01"
            assert bill_call["json"]["debit_bank"] == "MF1-0001"
            assert bill_call["json"]["pin_code"] == "1234"

    asyncio.run(run_test())


def test_async_merchant_client_verify_bill():
    async def run_test():
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 200
        mock_auth_resp.json.return_value = {
            "access_token": "token",
            "token_type": "Bearer",
        }

        mock_verify_resp = MagicMock()
        mock_verify_resp.status_code = 200
        mock_verify_resp.json.return_value = {
            "response_code": "00",
            "response_data": {
                "bill_code": "CODE-1234",
                "merchant_reference": "752000",
                "payment_reference": None,
                "status": "Paid",
            },
            "success": True,
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [mock_auth_resp, mock_verify_resp]
            client = AsyncMerchantClient("client_id", "client_secret")
            await client.authenticate()

            result = await client.verify_bill("CODE-1234", "752000", "1234")
            assert result["success"] is True
            assert result["response_data"]["status"] == "Paid"

            verify_call = mock_post.call_args_list[1][1]
            assert "json" in verify_call
            assert verify_call["json"]["bill_code"] == "CODE-1234"
            assert verify_call["json"]["merchant_reference"] == "752000"
            assert verify_call["json"]["pin_code"] == "1234"

    asyncio.run(run_test())


def test_async_merchant_client_cashin():
    async def run_test():
        mock_auth_resp = MagicMock()
        mock_auth_resp.status_code = 200
        mock_auth_resp.json.return_value = {
            "access_token": "token",
            "token_type": "Bearer",
        }

        mock_cashin_resp = MagicMock()
        mock_cashin_resp.status_code = 200
        mock_cashin_resp.json.return_value = {
            "response_code": "00",
            "response_data": {"reference": "REF-5678"},
            "success": True,
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [mock_auth_resp, mock_cashin_resp]
            client = AsyncMerchantClient("client_id", "client_secret")
            await client.authenticate()

            result = await client.cashin_client(
                bank_slug="MF1-0001",
                account="000016-01",
                amount=20000,
                merchant_reference="REF3223",
                description="Refunding customer",
                pin_code="1234",
            )
            assert result["success"] is True

            cashin_call = mock_post.call_args_list[1][1]
            assert "json" in cashin_call
            assert cashin_call["json"]["credit_bank"] == "MF1-0001"
            assert cashin_call["json"]["credit_account"] == "000016-01"
            assert cashin_call["json"]["currency"] == "BIF"
            assert cashin_call["json"]["pin_code"] == "1234"

    asyncio.run(run_test())

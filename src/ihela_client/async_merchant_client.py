import logging

import httpx

from .exceptions import iHelaAPIError, iHelaAuthenticationError
from .merchant_client import (
    iHela_BASE_TEST_URL,
    iHela_BASE_URL,
    iHela_ENDPOINTS,
    iHela_TOKEN_URL,
)

logger = logging.getLogger(__name__)


class AsyncMerchantClient:
    """Asynchronous iHela Merchant Client using httpx."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        state: str | None = None,
        prod: bool = False,
        ihela_url: str | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token_object = None
        self.state = state
        self.prod_env = prod

        self.ihela_base_url = ihela_url or (
            iHela_BASE_URL if prod else iHela_BASE_TEST_URL
        )

    def get_url(self, url: str) -> str:
        return self.ihela_base_url + str(url)

    async def get_response(self, resp: httpx.Response) -> dict:
        try:
            resp_json = resp.json()
            if not isinstance(resp_json, dict):
                resp_json = {"data": resp_json}
            resp_json["response_status"] = resp.status_code
            logger.debug(resp_json)
            return resp_json
        except (ValueError, KeyError, TypeError):
            logger.error(f"IHELA_CLIENT_ERROR : {resp.text}")
            raise iHelaAPIError(
                message="An error occurred while communicating with the iHela gateway.",
                status_code=resp.status_code,
                response_data=resp.text,
            ) from None

    async def get_auth_headers(self) -> dict[str, str]:
        await self.ensure_authenticated()
        if self.is_authenticated():
            return {
                "Authorization": "{} {}".format(
                    self.auth_token_object["token_type"],
                    self.auth_token_object["access_token"],
                )
            }
        return {}

    async def authenticate(self):
        url = iHela_TOKEN_URL
        auth_data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    self.get_url(url),
                    auth=(self.client_id, self.client_secret),
                    data=auth_data,
                )
                if resp.status_code != 200:
                    raise iHelaAuthenticationError(
                        f"Authentication failed with status code {resp.status_code}"
                    )
                self.auth_token_object = await self.get_response(resp)
            except httpx.HTTPError as e:
                raise iHelaAuthenticationError(
                    f"Connection to iHela gateway failed: {e}"
                ) from e

    def is_authenticated(self) -> bool:
        return (
            isinstance(self.auth_token_object, dict)
            and "access_token" in self.auth_token_object
        )

    async def ensure_authenticated(self):
        if not self.is_authenticated():
            await self.authenticate()

    async def customer_lookup(
        self,
        bank_slug: str,
        account_number: str | None = None,
        customer_id: str | None = None,
    ) -> dict:
        url = iHela_ENDPOINTS["LOOKUP"] % bank_slug
        query_param = account_number or customer_id
        async with httpx.AsyncClient() as client:
            headers = await self.get_auth_headers()
            resp = await client.get(
                self.get_url(url),
                params={"account_number": query_param},
                headers=headers,
            )
            return await self.get_response(resp)

    async def init_bill(
        self,
        amount: int,
        user: str,
        description: str,
        reference: str,
        bank: str | None = None,
        bank_client_id: str | None = None,
        redirect_uri: str | None = None,
    ) -> dict:
        await self.ensure_authenticated()
        if bank and not bank_client_id:
            bank_client_id = user
        bill_data = {
            "amount": str(amount),
            "description": description,
            "merchant_reference": reference,
            "user": user,
            "bank": bank,
            "bank_client_id": bank_client_id,
            "redirect_uri": redirect_uri,
        }
        bill_data = {k: v for k, v in bill_data.items() if v is not None}
        url = iHela_ENDPOINTS["BILL_INIT"]
        async with httpx.AsyncClient() as client:
            headers = await self.get_auth_headers()
            resp = await client.post(
                self.get_url(url),
                data=bill_data,
                headers=headers,
            )
            return await self.get_response(resp)

    async def verify_bill(self, code: str, reference: str) -> dict:
        await self.ensure_authenticated()
        bill_data = {"code": code, "reference": reference}
        url = iHela_ENDPOINTS["BILL_VERIFY"]
        async with httpx.AsyncClient() as client:
            headers = await self.get_auth_headers()
            resp = await client.post(
                self.get_url(url),
                data=bill_data,
                headers=headers,
            )
            return await self.get_response(resp)

    async def cashin_client(
        self,
        bank_slug: str,
        account: str,
        amount: int,
        merchant_reference: str,
        description: str,
    ) -> dict:
        await self.ensure_authenticated()
        cashin_data = {
            "bank_slug": bank_slug,
            "account": account,
            "amount": str(amount),
            "merchant_reference": merchant_reference,
            "description": description,
        }
        url = iHela_ENDPOINTS["CASHIN"]
        async with httpx.AsyncClient() as client:
            headers = await self.get_auth_headers()
            resp = await client.post(
                self.get_url(url),
                data=cashin_data,
                headers=headers,
            )
            return await self.get_response(resp)

    async def get_bank_list(self) -> dict:
        await self.ensure_authenticated()
        url = iHela_ENDPOINTS["BANKS_ALL"]
        async with httpx.AsyncClient() as client:
            headers = await self.get_auth_headers()
            resp = await client.get(self.get_url(url), headers=headers)
            return await self.get_response(resp)

    async def get_cashin_bank_list(self) -> dict:
        await self.ensure_authenticated()
        url = iHela_ENDPOINTS["BANKS_CASHIN"]
        async with httpx.AsyncClient() as client:
            headers = await self.get_auth_headers()
            resp = await client.get(self.get_url(url), headers=headers)
            return await self.get_response(resp)

    async def get_cashout_bank_list(self) -> dict:
        await self.ensure_authenticated()
        url = iHela_ENDPOINTS["BANKS_CASHOUT"]
        async with httpx.AsyncClient() as client:
            headers = await self.get_auth_headers()
            resp = await client.get(self.get_url(url), headers=headers)
            return await self.get_response(resp)

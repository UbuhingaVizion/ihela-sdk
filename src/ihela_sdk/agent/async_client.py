import logging
from typing import Any

import httpx

from ..core.exceptions import iHelaAPIError, iHelaAuthenticationError
from ..core.validators import validate_response

logger = logging.getLogger(__name__)

AGENT_ENDPOINTS = {
    "PING": "ihela/api/v1/ping/",
    "REFRESH": "ihela/api/v1/auth-token/refresh/",
    "AUTH_TOKEN": "ihela/api/v1/auth-token/",
    "LOOKUP": "ihela/api/v1/account-lookup/",
    "BALANCE": "ihela/api/v1/bsces/balance/",
    "DEPOSIT": "ihela/api/v1/agent-deposit/",
    "OPERATION_LOOKUP": "ihela/api/v1/operation-lookup/",
    "VALIDATE_WITHDRAWAL": "ihela/api/v1/validate-withdrawal/",
    "STATUS": "ihela/api/v1/transaction-status/",
}

iHela_BASE_URL = "https://gate.ihela.online/"
iHela_BASE_TEST_URL = "https://testgate.ihela.online/"
iHela_TOKEN_URL = "oAuth2/token/"


class AsyncAgentClient:
    """Asynchronous client for iHela Agent Services using httpx."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        prod: bool = False,
        ihela_url: str | None = None,
        ssl_cert: Any | None = None,
        signature_key: str | None = None,
        token: dict[str, Any] | None = None,
        auto_auth: bool = True,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token_object: dict[str, Any] | None = token
        self.prod_env = prod
        self.ssl_cert = ssl_cert
        self.signature_key = signature_key
        self.ihela_base_url = ihela_url or (
            iHela_BASE_URL if prod else iHela_BASE_TEST_URL
        )

    def get_url(self, url: str) -> str:
        return self.ihela_base_url + str(url)

    async def _get_response(self, resp: httpx.Response) -> dict[str, Any]:
        try:
            data: dict[str, Any] = resp.json()
            if not isinstance(data, dict):
                data = {"data": data}
            data["response_status"] = resp.status_code
            validate_response(data)
            return data
        except iHelaAPIError:
            raise
        except (ValueError, KeyError, TypeError):
            logger.error(f"IHELA_CLIENT_ERROR : {resp.text}")
            raise iHelaAPIError(
                status_code=resp.status_code,
                response_data=resp.text,
            ) from None

    async def get_auth_headers(self) -> dict[str, str]:
        await self.ensure_authenticated()
        if self.is_authenticated():
            assert self.auth_token_object is not None
            return {
                "Authorization": "{} {}".format(
                    self.auth_token_object["token_type"],
                    self.auth_token_object["access_token"],
                )
            }
        return {}

    async def authenticate(self) -> None:
        url = iHela_TOKEN_URL
        auth_data = {"grant_type": "client_credentials"}
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
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
                self.auth_token_object = await self._get_response(resp)
            except httpx.HTTPError as e:
                raise iHelaAuthenticationError(
                    f"Connection to iHela gateway failed: {e}"
                ) from e

    async def refresh_token(self) -> None:
        if not self.is_authenticated():
            raise iHelaAuthenticationError("No valid refresh token available.")
        assert self.auth_token_object is not None
        if "refresh_token" not in self.auth_token_object:
            raise iHelaAuthenticationError("No valid refresh token available.")
        url = AGENT_ENDPOINTS["REFRESH"]
        refresh_data = {"refresh": self.auth_token_object["refresh_token"]}
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            try:
                resp = await client.post(
                    self.get_url(url),
                    data=refresh_data,
                    headers={
                        "Authorization": f"Bearer {self.auth_token_object['access_token']}"
                    },
                )
                if resp.status_code != 200:
                    raise iHelaAuthenticationError("Token refresh failed.")
                refresh_response = await self._get_response(resp)
                self.auth_token_object["access_token"] = refresh_response["access"]
            except httpx.HTTPError as e:
                raise iHelaAuthenticationError(
                    f"Connection failed during token refresh: {e}"
                ) from e

    def is_authenticated(self) -> bool:
        return (
            isinstance(self.auth_token_object, dict)
            and "access_token" in self.auth_token_object
        )

    async def ensure_authenticated(self) -> None:
        if not self.is_authenticated():
            await self.authenticate()

    def clear_token(self) -> None:
        self.auth_token_object = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} prod_env={self.prod_env}>"

    async def request_token(self, username: str, password: str) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["AUTH_TOKEN"]
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            resp = await client.post(
                self.get_url(url),
                json={"username": username, "password": password},
            )
            token_data = await self._get_response(resp)
            self.auth_token_object = token_data
            return token_data

    async def ping(self) -> dict[str, Any]:
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.get(
                self.get_url(AGENT_ENDPOINTS["PING"]), headers=headers
            )
            return await self._get_response(resp)

    async def account_lookup(self, account_number: str) -> dict[str, Any]:
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.post(
                self.get_url(AGENT_ENDPOINTS["LOOKUP"]),
                json={"account_number": account_number},
                headers=headers,
            )
            return await self._get_response(resp)

    async def account_balance(self, account_number: str) -> dict[str, Any]:
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.post(
                self.get_url(AGENT_ENDPOINTS["BALANCE"]),
                json={"account_number": account_number},
                headers=headers,
            )
            return await self._get_response(resp)

    async def deposit(
        self,
        credit_account: str,
        credit_account_holder: str,
        amount: float,
        description: str,
        external_reference: str = "",
        pin_code: str = "",
        external_code: str = "",
    ) -> dict[str, Any]:
        from ..core.security import DepositPayload, generate_signature

        validated = DepositPayload(
            credit_account=credit_account,
            credit_account_holder=credit_account_holder,
            amount=amount,
            description=description,
            external_reference=external_reference or __import__("uuid").uuid4().hex,
            pin_code=pin_code,
            external_code=external_code,
        )
        payload = validated.model_dump()
        headers = await self.get_auth_headers()
        if self.signature_key:
            import json

            signature = generate_signature(json.dumps(payload), self.signature_key)
            headers["X-iHela-Signature"] = signature
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            resp = await client.post(
                self.get_url(AGENT_ENDPOINTS["DEPOSIT"]),
                json=payload,
                headers=headers,
            )
            return await self._get_response(resp)

    async def operation_lookup(
        self, operation_code: str, amount: str
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.post(
                self.get_url(AGENT_ENDPOINTS["OPERATION_LOOKUP"]),
                json={"operation_code": operation_code, "amount": amount},
                headers=headers,
            )
            return await self._get_response(resp)

    async def validate_withdrawal(
        self,
        external_reference: str,
        pin_code: str,
        agent_code: str,
        amount: str,
        external_code: str,
        validation_operation_code: str,
    ) -> dict[str, Any]:
        from ..core.security import ValidateWithdrawalPayload, generate_signature

        validated = ValidateWithdrawalPayload(
            external_reference=external_reference,
            pin_code=pin_code,
            agent_code=agent_code,
            amount=amount,
            external_code=external_code,
            validation_operation_code=validation_operation_code,
        )
        payload = validated.model_dump()
        headers = await self.get_auth_headers()
        if self.signature_key:
            import json

            signature = generate_signature(json.dumps(payload), self.signature_key)
            headers["X-iHela-Signature"] = signature
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            resp = await client.post(
                self.get_url(AGENT_ENDPOINTS["VALIDATE_WITHDRAWAL"]),
                json=payload,
                headers=headers,
            )
            return await self._get_response(resp)

    async def transaction_status(
        self, external_reference: str, reference: str
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.post(
                self.get_url(AGENT_ENDPOINTS["STATUS"]),
                json={"external_reference": external_reference, "reference": reference},
                headers=headers,
            )
            return await self._get_response(resp)

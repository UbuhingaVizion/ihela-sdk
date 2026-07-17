import logging
from typing import Any

import httpx

from .exceptions import iHelaAPIError, iHelaAuthenticationError
from .merchant_client import iHela_BASE_TEST_URL, iHela_BASE_URL, iHela_TOKEN_URL
from .security import (
    DepositPayload,
    ValidateWithdrawalPayload,
    generate_signature,
    mask_sensitive_data,
)

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


class AgentClient:
    """Synchronous client for iHela Agent Services."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        prod: bool = False,
        ihela_url: str | None = None,
        ssl_cert: Any | None = None,
        signature_key: str | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token_object: dict[str, Any] | None = None
        self.prod_env = prod
        self.ssl_cert = ssl_cert
        self.signature_key = signature_key
        self.ihela_base_url = ihela_url or (
            iHela_BASE_URL if prod else iHela_BASE_TEST_URL
        )

    def get_url(self, url: str) -> str:
        return self.ihela_base_url + str(url)

    def get_response(self, resp: httpx.Response) -> dict[str, Any]:
        try:
            resp_json = resp.json()
            if not isinstance(resp_json, dict):
                resp_json = {"data": resp_json}
            resp_json["response_status"] = resp.status_code
            logger.debug(mask_sensitive_data(resp_json))
            return resp_json
        except (ValueError, KeyError, TypeError):
            logger.error(f"IHELA_CLIENT_ERROR : {resp.text}")
            raise iHelaAPIError(
                message="An error occurred while communicating with the iHela gateway.",
                status_code=resp.status_code,
                response_data=resp.text,
            ) from None

    def get_auth_headers(self) -> dict[str, str]:
        self.ensure_authenticated()
        if self.is_authenticated():
            assert self.auth_token_object is not None
            return {
                "Authorization": "{} {}".format(
                    self.auth_token_object["token_type"],
                    self.auth_token_object["access_token"],
                )
            }
        return {}

    def authenticate(self):
        url = iHela_TOKEN_URL
        auth_data = {"grant_type": "client_credentials"}
        try:
            with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
                resp = client.post(
                    self.get_url(url),
                    auth=(self.client_id, self.client_secret),
                    data=auth_data,
                )
            if resp.status_code != 200:
                raise iHelaAuthenticationError(
                    f"Authentication failed with status code {resp.status_code}"
                )
            self.auth_token_object = self.get_response(resp)
        except httpx.HTTPError as e:
            raise iHelaAuthenticationError(
                f"Connection to iHela gateway failed: {e}"
            ) from e

    def refresh_token(self):
        if not self.is_authenticated() or "refresh_token" not in self.auth_token_object:
            raise iHelaAuthenticationError("No valid refresh token available.")

        url = AGENT_ENDPOINTS["REFRESH"]
        refresh_data = {"refresh": self.auth_token_object["refresh_token"]}
        try:
            with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
                resp = client.post(
                    self.get_url(url),
                    data=refresh_data,
                    headers={
                        "Authorization": f"Bearer {self.auth_token_object['access_token']}"
                    },
                )
            if resp.status_code != 200:
                raise iHelaAuthenticationError("Token refresh failed.")
            refresh_response = self.get_response(resp)
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

    def ensure_authenticated(self):
        if not self.is_authenticated():
            self.authenticate()

    def request_token(self, username: str, password: str) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["AUTH_TOKEN"]
        payload = {"username": username, "password": password}
        with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
            resp = client.post(self.get_url(url), json=payload)
        token_data = self.get_response(resp)
        self.auth_token_object = token_data
        return token_data

    def ping(self) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["PING"]
        with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
            resp = client.get(
                self.get_url(url),
                headers=self.get_auth_headers(),
            )
        return self.get_response(resp)

    def account_lookup(self, account_number: str) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["LOOKUP"]
        payload = {"account_number": account_number}
        with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
            resp = client.post(
                self.get_url(url),
                json=payload,
                headers=self.get_auth_headers(),
            )
        return self.get_response(resp)

    def account_balance(self, account_number: str) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["BALANCE"]
        payload = {"account_number": account_number}
        with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
            resp = client.post(
                self.get_url(url),
                json=payload,
                headers=self.get_auth_headers(),
            )
        return self.get_response(resp)

    def deposit(
        self,
        credit_account: str,
        credit_account_holder: str,
        amount: float,
        description: str,
        external_reference: str,
        pin_code: str,
        external_code: str = "",
    ) -> dict[str, Any]:
        validated = DepositPayload(
            credit_account=credit_account,
            credit_account_holder=credit_account_holder,
            amount=amount,
            description=description,
            external_reference=external_reference,
            pin_code=pin_code,
            external_code=external_code,
        )
        payload = validated.model_dump()
        url = AGENT_ENDPOINTS["DEPOSIT"]
        headers = self.get_auth_headers()
        if self.signature_key:
            import json

            signature = generate_signature(json.dumps(payload), self.signature_key)
            headers["X-iHela-Signature"] = signature

        with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
            resp = client.post(
                self.get_url(url),
                json=payload,
                headers=headers,
            )
        return self.get_response(resp)

    def operation_lookup(self, operation_code: str, amount: str) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["OPERATION_LOOKUP"]
        payload = {
            "operation_code": operation_code,
            "amount": amount,
        }
        with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
            resp = client.post(
                self.get_url(url),
                json=payload,
                headers=self.get_auth_headers(),
            )
        return self.get_response(resp)

    def validate_withdrawal(
        self,
        external_reference: str,
        pin_code: str,
        agent_code: str,
        amount: str,
        external_code: str,
        validation_operation_code: str,
    ) -> dict[str, Any]:
        validated = ValidateWithdrawalPayload(
            external_reference=external_reference,
            pin_code=pin_code,
            agent_code=agent_code,
            amount=amount,
            external_code=external_code,
            validation_operation_code=validation_operation_code,
        )
        payload = validated.model_dump()
        url = AGENT_ENDPOINTS["VALIDATE_WITHDRAWAL"]
        headers = self.get_auth_headers()
        if self.signature_key:
            import json

            signature = generate_signature(json.dumps(payload), self.signature_key)
            headers["X-iHela-Signature"] = signature

        with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
            resp = client.post(
                self.get_url(url),
                json=payload,
                headers=headers,
            )
        return self.get_response(resp)

    def transaction_status(
        self, external_reference: str, reference: str
    ) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["STATUS"]
        payload = {
            "external_reference": external_reference,
            "reference": reference,
        }
        with httpx.Client(cert=self.ssl_cert, timeout=5.0) as client:
            resp = client.post(
                self.get_url(url),
                json=payload,
                headers=self.get_auth_headers(),
            )
        return self.get_response(resp)


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
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token_object: dict[str, Any] | None = None
        self.prod_env = prod
        self.ssl_cert = ssl_cert
        self.signature_key = signature_key
        self.ihela_base_url = ihela_url or (
            iHela_BASE_URL if prod else iHela_BASE_TEST_URL
        )

    def get_url(self, url: str) -> str:
        return self.ihela_base_url + str(url)

    async def get_response(self, resp: httpx.Response) -> dict[str, Any]:
        try:
            resp_json = resp.json()
            if not isinstance(resp_json, dict):
                resp_json = {"data": resp_json}
            resp_json["response_status"] = resp.status_code
            logger.debug(mask_sensitive_data(resp_json))
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
            assert self.auth_token_object is not None
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
                self.auth_token_object = await self.get_response(resp)
            except httpx.HTTPError as e:
                raise iHelaAuthenticationError(
                    f"Connection to iHela gateway failed: {e}"
                ) from e

    async def refresh_token(self):
        if not self.is_authenticated() or "refresh_token" not in self.auth_token_object:
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
                refresh_response = await self.get_response(resp)
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

    async def ensure_authenticated(self):
        if not self.is_authenticated():
            await self.authenticate()

    async def request_token(self, username: str, password: str) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["AUTH_TOKEN"]
        payload = {"username": username, "password": password}
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            resp = await client.post(self.get_url(url), json=payload)
            token_data = await self.get_response(resp)
            self.auth_token_object = token_data
            return token_data

    async def ping(self) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["PING"]
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.get(self.get_url(url), headers=headers)
            return await self.get_response(resp)

    async def account_lookup(self, account_number: str) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["LOOKUP"]
        payload = {"account_number": account_number}
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.post(self.get_url(url), json=payload, headers=headers)
            return await self.get_response(resp)

    async def account_balance(self, account_number: str) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["BALANCE"]
        payload = {"account_number": account_number}
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.post(self.get_url(url), json=payload, headers=headers)
            return await self.get_response(resp)

    async def deposit(
        self,
        credit_account: str,
        credit_account_holder: str,
        amount: float,
        description: str,
        external_reference: str,
        pin_code: str,
        external_code: str = "",
    ) -> dict[str, Any]:
        validated = DepositPayload(
            credit_account=credit_account,
            credit_account_holder=credit_account_holder,
            amount=amount,
            description=description,
            external_reference=external_reference,
            pin_code=pin_code,
            external_code=external_code,
        )
        payload = validated.model_dump()
        url = AGENT_ENDPOINTS["DEPOSIT"]
        headers = await self.get_auth_headers()
        if self.signature_key:
            import json

            signature = generate_signature(json.dumps(payload), self.signature_key)
            headers["X-iHela-Signature"] = signature

        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            resp = await client.post(self.get_url(url), json=payload, headers=headers)
            return await self.get_response(resp)

    async def operation_lookup(
        self, operation_code: str, amount: str
    ) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["OPERATION_LOOKUP"]
        payload = {
            "operation_code": operation_code,
            "amount": amount,
        }
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.post(self.get_url(url), json=payload, headers=headers)
            return await self.get_response(resp)

    async def validate_withdrawal(
        self,
        external_reference: str,
        pin_code: str,
        agent_code: str,
        amount: str,
        external_code: str,
        validation_operation_code: str,
    ) -> dict[str, Any]:
        validated = ValidateWithdrawalPayload(
            external_reference=external_reference,
            pin_code=pin_code,
            agent_code=agent_code,
            amount=amount,
            external_code=external_code,
            validation_operation_code=validation_operation_code,
        )
        payload = validated.model_dump()
        url = AGENT_ENDPOINTS["VALIDATE_WITHDRAWAL"]
        headers = await self.get_auth_headers()
        if self.signature_key:
            import json

            signature = generate_signature(json.dumps(payload), self.signature_key)
            headers["X-iHela-Signature"] = signature

        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            resp = await client.post(self.get_url(url), json=payload, headers=headers)
            return await self.get_response(resp)

    async def transaction_status(
        self, external_reference: str, reference: str
    ) -> dict[str, Any]:
        url = AGENT_ENDPOINTS["STATUS"]
        payload = {
            "external_reference": external_reference,
            "reference": reference,
        }
        async with httpx.AsyncClient(cert=self.ssl_cert, timeout=5.0) as client:
            headers = await self.get_auth_headers()
            resp = await client.post(self.get_url(url), json=payload, headers=headers)
            return await self.get_response(resp)

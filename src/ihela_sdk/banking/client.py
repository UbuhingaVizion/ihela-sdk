import json
import logging
from typing import Any

import httpx

from ..core.base import BaseClient
from ..core.exceptions import iHelaAPIError, iHelaAuthenticationError
from ..core.security import (
    DepositPayload,
    WithdrawalPayload,
    generate_signature,
    mask_sensitive_data,
)
from ..core.validators import validate_response

logger = logging.getLogger(__name__)

iHela_BASE_URL = "https://gate.ihela.online/"
iHela_BASE_TEST_URL = "https://testgate.ihela.online/"
iHela_TOKEN_URL = "oAuth2/token/"

BANKING_ENDPOINTS = {
    "PING": "ihela/api/v1/ping/",
    "REFRESH": "ihela/api/v1/auth-token/refresh/",
    "AUTH_TOKEN": "ihela/api/v1/auth-token/",
    "LOOKUP": "ihela/api/v1/account-lookup/",
    "BALANCE": "ihela/api/v1/bsces/balance/",
    "DEPOSIT": "ihela/api/v1/make-deposit/",
    "WITHDRAWAL": "ihela/api/v1/make-withdrawal/",
    "STATEMENT": "ihela/api/v1/mini-statement/",
    "STATUS": "ihela/api/v1/transaction-status/",
    "TRANSACTION_FEE": "ihela/api/v1/transaction-fee/",
}


class BankingClient(BaseClient):
    """Synchronous client for iHela Banking Services.

    Provides connection pooling, User-Agent header, circuit breaker, and
    response code validation out of the box. Optional rate limiting via
    ``rate_limit`` parameter.
    """

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
        rate_limit: int = 0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_cooldown: float = 30.0,
    ):
        base_url = ihela_url or (iHela_BASE_URL if prod else iHela_BASE_TEST_URL)
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            prod=prod,
            ihela_base_url=base_url,
            ssl_cert=ssl_cert,
            signature_key=signature_key,
            rate_limit=rate_limit,
            circuit_breaker_threshold=circuit_breaker_threshold,
            circuit_breaker_cooldown=circuit_breaker_cooldown,
        )
        self.auth_token_object: dict[str, Any] | None = token
        if auto_auth and token is None:
            self.authenticate()

    def get_url(self, url: str) -> str:
        return self.ihela_base_url + str(url)

    def _get_response(self, resp: httpx.Response) -> dict[str, Any]:
        try:
            data: dict[str, Any] = resp.json()
            if not isinstance(data, dict):
                data = {"data": data}
            data["response_status"] = resp.status_code
            logger.debug(mask_sensitive_data(data))
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

    def authenticate(self) -> None:
        url = iHela_TOKEN_URL
        auth_data = {"grant_type": "client_credentials"}
        try:
            resp = self._request(
                "POST",
                self.get_url(url),
                data=auth_data,
                auth=(self.client_id, self.client_secret),
            )
            if resp.status_code != 200:
                raise iHelaAuthenticationError(
                    f"Authentication failed with status code {resp.status_code}"
                )
            self.auth_token_object = self._get_response(resp)
        except httpx.HTTPError as e:
            raise iHelaAuthenticationError(
                f"Connection to iHela gateway failed: {e}"
            ) from e

    def refresh_token(self) -> None:
        if not self.is_authenticated():
            raise iHelaAuthenticationError("No valid refresh token available.")
        assert self.auth_token_object is not None
        if "refresh_token" not in self.auth_token_object:
            raise iHelaAuthenticationError("No valid refresh token available.")
        url = BANKING_ENDPOINTS["REFRESH"]
        refresh_data = {"refresh": self.auth_token_object["refresh_token"]}
        try:
            resp = self._request(
                "POST",
                self.get_url(url),
                data=refresh_data,
                headers={
                    "Authorization": f"Bearer {self.auth_token_object['access_token']}"
                },
            )
            if resp.status_code != 200:
                raise iHelaAuthenticationError("Token refresh failed.")
            refresh_response = self._get_response(resp)
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

    def ensure_authenticated(self) -> None:
        if not self.is_authenticated():
            self.authenticate()

    def clear_token(self) -> None:
        self.auth_token_object = None

    # --- API methods ---

    def request_token(self, username: str, password: str) -> dict[str, Any]:
        url = BANKING_ENDPOINTS["AUTH_TOKEN"]
        payload = {"username": username, "password": password}
        resp = self._request("POST", self.get_url(url), json=payload)
        token_data = self._get_response(resp)
        self.auth_token_object = token_data
        return token_data

    def ping(self) -> dict[str, Any]:
        resp = self._request(
            "GET",
            self.get_url(BANKING_ENDPOINTS["PING"]),
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def transaction_fee(
        self, currency: str, operation_type: str, amount: str
    ) -> dict[str, Any]:
        resp = self._request(
            "POST",
            self.get_url(BANKING_ENDPOINTS["TRANSACTION_FEE"]),
            json={
                "currency": currency,
                "operation_type": operation_type,
                "amount": amount,
            },
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def account_lookup(self, account_number: str) -> dict[str, Any]:
        resp = self._request(
            "POST",
            self.get_url(BANKING_ENDPOINTS["LOOKUP"]),
            json={"account_number": account_number},
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def account_balance(self, account_number: str) -> dict[str, Any]:
        resp = self._request(
            "POST",
            self.get_url(BANKING_ENDPOINTS["BALANCE"]),
            json={"account_number": account_number},
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def deposit(
        self,
        credit_account: str,
        credit_account_holder: str,
        amount: float,
        description: str,
        external_reference: str = "",
        pin_code: str = "",
        external_code: str = "",
    ) -> dict[str, Any]:
        validated = DepositPayload(
            credit_account=credit_account,
            credit_account_holder=credit_account_holder,
            amount=amount,
            description=description,
            external_reference=external_reference or self._generate_reference(),
            pin_code=pin_code,
            external_code=external_code,
        )
        payload = validated.model_dump()
        headers = self.get_auth_headers()
        if self.signature_key:
            signature = generate_signature(json.dumps(payload), self.signature_key)
            headers["X-iHela-Signature"] = signature
        resp = self._request(
            "POST",
            self.get_url(BANKING_ENDPOINTS["DEPOSIT"]),
            json=payload,
            headers=headers,
        )
        return self._get_response(resp)

    def withdrawal(
        self,
        debit_account: str,
        debit_account_holder: str,
        amount: float,
        description: str,
        external_reference: str = "",
        pin_code: str = "",
    ) -> dict[str, Any]:
        validated = WithdrawalPayload(
            debit_account=debit_account,
            debit_account_holder=debit_account_holder,
            amount=amount,
            description=description,
            external_reference=external_reference or self._generate_reference(),
            pin_code=pin_code,
        )
        payload = validated.model_dump()
        headers = self.get_auth_headers()
        if self.signature_key:
            signature = generate_signature(json.dumps(payload), self.signature_key)
            headers["X-iHela-Signature"] = signature
        resp = self._request(
            "POST",
            self.get_url(BANKING_ENDPOINTS["WITHDRAWAL"]),
            json=payload,
            headers=headers,
        )
        return self._get_response(resp)

    def statement(self, account_number: str) -> dict[str, Any]:
        resp = self._request(
            "GET",
            self.get_url(BANKING_ENDPOINTS["STATEMENT"]),
            params={"account_number": account_number},
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def transaction_status(
        self, external_reference: str, reference: str
    ) -> dict[str, Any]:
        resp = self._request(
            "POST",
            self.get_url(BANKING_ENDPOINTS["STATUS"]),
            json={"external_reference": external_reference, "reference": reference},
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

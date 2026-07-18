import json
import logging
from typing import Any

import httpx

from ..core.base import BaseClient
from ..core.exceptions import iHelaAPIError

logger = logging.getLogger(__name__)

iHela_BASE_URL = "https://gate.ihela.online/"
iHela_BASE_TEST_URL = "https://testgate.ihela.online/"
iHela_TOKEN_URL = "oAuth2/token/"

ENDPOINTS = {
    "USER_INFO": "api/v1/connected-user/",
    "BILL_INIT": "api/v1/payments/bill-init/",
    "BILL_VERIFY": "api/v1/payments/bill-check/",
    "CASHIN": "api/v1/payments/cash-in/",
    "BANKS_ALL": "api/v1/payments/bank/",
    "BANKS_CASHIN": "api/v1/payments/bank/cashin/",
    "BANKS_CASHOUT": "api/v1/payments/bank/cashout/",
    "LOOKUP": "api/v1/bank/%s/account/lookup/",
}


class MerchantClient(BaseClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        state: str | None = None,
        prod: bool = False,
        ihela_url: str | None = None,
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
            rate_limit=rate_limit,
            circuit_breaker_threshold=circuit_breaker_threshold,
            circuit_breaker_cooldown=circuit_breaker_cooldown,
        )
        self.auth_token_object: dict[str, Any] | None = token
        self.redirect_uri: str | None = None
        self.state = state
        if auto_auth and token is None:
            self.authenticate()

    def _get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("POST", path, **kwargs)

    def get_url(self, path: str) -> str:
        return self.ihela_base_url + str(path)

    def _get_response(self, resp: httpx.Response) -> dict[str, Any]:
        try:
            data: dict[str, Any] = dict(resp.json())
            data["response_status"] = resp.status_code
            from ..core.validators import validate_response

            return validate_response(data)
        except iHelaAPIError:
            raise
        except json.decoder.JSONDecodeError:
            logger.error(f"IHELA_CLIENT_ERROR : {resp.text}")
            return {"errors": {"request": "An error occurred during request"}}

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

    def ensure_authenticated(self) -> None:
        if not self.is_authenticated():
            self.authenticate()

    def authenticate(self) -> httpx.Response:
        auth_data = {"grant_type": "client_credentials"}
        resp = self._post(
            self.get_url(iHela_TOKEN_URL),
            data=auth_data,
            auth=(self.client_id, self.client_secret),
        )
        self.auth_token_object = self._get_response(resp)
        return resp

    def is_authenticated(self) -> bool:
        return (
            isinstance(self.auth_token_object, dict)
            and "access_token" in self.auth_token_object
        )

    def get_access_token(self) -> str | None:
        if self.is_authenticated() and self.auth_token_object is not None:
            return self.auth_token_object.get("access_token")  # type: ignore[return-value]
        return None

    def get_token_type(self) -> str | None:
        if self.is_authenticated() and self.auth_token_object is not None:
            return self.auth_token_object.get("token_type")  # type: ignore[return-value]
        return None

    def clear_token(self) -> None:
        self.auth_token_object = None

    def customer_lookup(
        self,
        bank_slug: str,
        customer_id: str | None = None,
        account_number: str | None = None,
    ) -> dict[str, Any]:
        url = ENDPOINTS["LOOKUP"] % bank_slug
        query_param = account_number or customer_id
        resp = self._get(
            self.get_url(url),
            params={"account_number": query_param},
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def init_bill(
        self,
        amount: int,
        user: str,
        description: str,
        reference: str,
        bank: str | None = None,
        bank_client_id: str | None = None,
        redirect_uri: str | None = None,
        pin_code: str | None = None,
        merchant_description: str | None = None,
        payment_product_id: str | None = None,
    ) -> dict[str, Any]:
        if not self.is_authenticated():
            return {"errors": {"authentication": "The client is not authenticated"}}
        bill_data: dict[str, Any] = {
            "debit_bank": bank,
            "debit_account": user,
            "amount": amount,
            "description": description,
            "merchant_description": merchant_description or description,
            "merchant_reference": reference,
            "redirect_uri": redirect_uri,
            "payment_product_id": payment_product_id,
            "pin_code": pin_code,
        }
        bill_data = {k: v for k, v in bill_data.items() if v is not None}
        resp = self._post(
            self.get_url(ENDPOINTS["BILL_INIT"]),
            json=bill_data,
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def verify_bill(
        self, bill_code: str, merchant_reference: str, pin_code: str
    ) -> dict[str, Any]:
        resp = self._post(
            self.get_url(ENDPOINTS["BILL_VERIFY"]),
            json={
                "bill_code": bill_code,
                "merchant_reference": merchant_reference,
                "pin_code": pin_code,
            },
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def cashin_client(
        self,
        bank_slug: str,
        account: str,
        amount: int,
        merchant_reference: str,
        description: str,
        pin_code: str | None = None,
        credit_account_holder: str | None = None,
        currency: str = "BIF",
    ) -> dict[str, Any]:
        if not self.is_authenticated():
            return {"errors": {"authentication": "The client is not authenticated"}}
        cashin_data: dict[str, Any] = {
            "credit_bank": bank_slug,
            "credit_account": account,
            "credit_account_holder": credit_account_holder or account,
            "amount": amount,
            "merchant_reference": merchant_reference,
            "description": description,
            "pin_code": pin_code,
            "currency": currency,
        }
        cashin_data = {k: v for k, v in cashin_data.items() if v is not None}
        resp = self._post(
            self.get_url(ENDPOINTS["CASHIN"]),
            json=cashin_data,
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def get_bank_list(self) -> dict[str, Any]:
        if not self.is_authenticated():
            return {"errors": {"authentication": "The client is not authenticated"}}
        resp = self._get(
            self.get_url(ENDPOINTS["BANKS_ALL"]),
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def get_cashin_bank_list(self) -> dict[str, Any]:
        if not self.is_authenticated():
            return {"errors": {"authentication": "The client is not authenticated"}}
        resp = self._get(
            self.get_url(ENDPOINTS["BANKS_CASHIN"]),
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def get_cashout_bank_list(self) -> dict[str, Any]:
        if not self.is_authenticated():
            return {"errors": {"authentication": "The client is not authenticated"}}
        resp = self._get(
            self.get_url(ENDPOINTS["BANKS_CASHOUT"]),
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

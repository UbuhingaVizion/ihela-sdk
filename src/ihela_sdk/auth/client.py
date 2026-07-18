import json
import logging
import secrets
import string
import urllib.parse
from typing import Any

import httpx

from ..core.base import BaseClient
from ..core.exceptions import iHelaAPIError

logger = logging.getLogger(__name__)

iHela_BASE_URL = "https://gate.ihela.online/"
iHela_BASE_TEST_URL = "https://testgate.ihela.online/"
iHela_TOKEN_URL = "oAuth2/token/"
iHela_AUTH_URL = "oAuth2/authorize/"

ENDPOINTS = {
    "USER_INFO": "api/v1/connected-user/",
    "BILL_INIT": "api/v1/payments/bill-init/",
    "BILL_VERIFY": "api/v1/payments/bill-check/",
}


class MerchantAuthorizationClient(BaseClient):
    """OAuth2 Authorization Code client for user-facing flows.

    Handles the full authorization_code grant: generate login URLs,
    exchange codes for tokens, and fetch user info.
    """

    provider_name = "iHelá"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        state: str | None = None,
        prod: bool | None = None,
        ihela_url: str | None = None,
        token: dict[str, Any] | None = None,
        auto_auth: bool = True,
        rate_limit: int = 0,
    ):
        base_url = iHela_BASE_URL
        if prod is False:
            base_url = iHela_BASE_TEST_URL
        if prod is True:
            base_url = iHela_BASE_URL
        if ihela_url:
            base_url = ihela_url
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            prod=prod or False,
            ihela_base_url=base_url,
            rate_limit=rate_limit,
        )
        self.auth_token_object: dict[str, Any] | None = token
        self.user_object: dict[str, Any] | None = None
        self.redirect_uri: str | None = None
        self.state = state

    def _get_response(self, resp: httpx.Response) -> dict[str, Any]:
        try:
            data: dict[str, Any] = dict(resp.json())
            data["response_status"] = resp.status_code
            logger.debug(data)
            return data
        except json.decoder.JSONDecodeError:
            logger.error(f"IHELA_CLIENT_ERROR : {resp.text}")
            return {"errors": {"request": "An error occurred during request"}}

    def get_url(self, url: str) -> str:
        return self.ihela_base_url + str(url)

    def get_auth_headers(self) -> dict[str, str]:
        if self.is_authenticated():
            assert self.auth_token_object is not None
            return {
                "Authorization": "{} {}".format(
                    self.auth_token_object["token_type"],
                    self.auth_token_object["access_token"],
                )
            }
        return {}

    def get_authorization_url(
        self, redirect_uri: str, state_: str | None = None
    ) -> str:
        response_type = "code"
        if not self.redirect_uri or self.redirect_uri != redirect_uri:
            self.redirect_uri = redirect_uri
        chars = string.ascii_lowercase + string.digits + string.ascii_uppercase
        if not self.state:
            self.state = "".join(secrets.choice(chars) for _ in range(20))
        auth_dict = {
            "state": self.state,
            "response_type": response_type,
            "client_id": self.client_id,
            "redirect_uri": urllib.parse.quote(redirect_uri),
        }
        params = (
            f"state={auth_dict['state']}"
            f"&response_type={auth_dict['response_type']}"
            f"&client_id={auth_dict['client_id']}"
            f"&redirect_uri={auth_dict['redirect_uri']}"
        )
        return self.get_url(iHela_AUTH_URL) + "?" + params

    def authenticate(
        self, authorization_code: str, redirect_uri: str
    ) -> httpx.Response:
        auth_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
        }
        try:
            resp = self._request("POST", self.get_url(iHela_TOKEN_URL), data=auth_data)
            self.auth_token_object = self._get_response(resp)
            self.get_user_info()
            return resp
        except iHelaAPIError:
            raise

    def is_authenticated(self) -> bool:
        return (
            isinstance(self.auth_token_object, dict)
            and self.auth_token_object.get("access_token") is not None
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
        self.user_object = None

    def get_user_info(self) -> dict[str, Any] | None:
        if self.is_authenticated():
            resp = self._request(
                "GET",
                self.get_url(ENDPOINTS["USER_INFO"]),
                headers=self.get_auth_headers(),
            )
            self.user_object = self._get_response(resp)
            return self.user_object
        return None

    def bill_init(
        self, amount: int, description: str, reference: str, redirect_uri: str
    ) -> dict[str, Any]:
        if not self.is_authenticated():
            return {"errors": {"authentication": "The client is not authenticated"}}
        bill_data = {
            "debit_account": "",
            "amount": amount,
            "description": description,
            "merchant_description": description,
            "merchant_reference": reference,
            "redirect_uri": redirect_uri,
            "payment_product_id": None,
        }
        resp = self._request(
            "POST",
            self.get_url(ENDPOINTS["BILL_INIT"]),
            json=bill_data,
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

    def bill_verify(
        self, bill_code: str, merchant_reference: str, pin_code: str | None = None
    ) -> dict[str, Any]:
        bill_data = {
            "bill_code": bill_code,
            "merchant_reference": merchant_reference,
            "pin_code": pin_code,
        }
        resp = self._request(
            "POST",
            self.get_url(ENDPOINTS["BILL_VERIFY"]),
            json=bill_data,
            headers=self.get_auth_headers(),
        )
        return self._get_response(resp)

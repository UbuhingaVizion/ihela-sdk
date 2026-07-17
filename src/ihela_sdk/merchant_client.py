"""
Pierre-Claver Koko Banywerha

UbuViz (c) 2019
info@ubuviz.com

Python client for integration
"""

import json
import logging

try:
    import secrets
except ImportError:  # Python < 3.6
    import random as secrets

import requests

logger = logging.getLogger(__name__)


iHela_BASE_URL = "https://gate.ihela.online/"
iHela_BASE_TEST_URL = "https://testgate.ihela.online/"
iHela_TOKEN_URL = "oAuth2/token/"
iHela_AUTH_URL = "oAuth2/authorize/"


iHela_ENDPOINTS = {
    "USER_INFO": "api/v1/connected-user/",
    "BILL_INIT": "api/v1/payments/bill-init/",
    "BILL_VERIFY": "api/v1/payments/bill-check/",
    "CASHIN": "api/v1/payments/cash-in/",
    "BANKS_ALL": "api/v1/payments/bank/",
    "BANKS_CASHIN": "api/v1/payments/bank/cashin/",
    "BANKS_CASHOUT": "api/v1/payments/bank/cashout/",
    "LOOKUP": "api/v1/bank/%s/account/lookup/",
}


class MerchantClient:
    def __init__(
        self, client_id, client_secret, state=None, prod=False, ihela_url=None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token_object = None
        self.redirect_uri = None
        self.state = state
        self.prod_env = prod

        self.ihela_base_url = iHela_BASE_URL

        if ihela_url:
            self.ihela_base_url = ihela_url

        elif self.prod_env is True:
            self.ihela_base_url = iHela_BASE_URL

        elif self.prod_env is False:
            self.ihela_base_url = iHela_BASE_TEST_URL

        else:
            self.ihela_base_url = iHela_BASE_TEST_URL

        self.authenticate()

    def get_response(self, resp):
        try:
            resp_json = dict(resp.json())
            resp_json["response_status"] = resp.status_code
            logger.debug(resp_json)
            return resp_json
        except json.decoder.JSONDecodeError:
            logger.error(f"IHELA_CLIENT_ERROR : {resp.text}")
            return {"errors": {"request": "An error occured during request"}}

    def get_url(self, url):
        return self.ihela_base_url + str(url)

    def get_auth_headers(self):
        if self.is_authenticated():
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

        if not self.prod_env:
            logger.debug(auth_data)

        auth_ = requests.post(
            self.get_url(url),
            auth=(self.client_id, self.client_secret),
            data=auth_data,
            timeout=15.0,
        )
        self.auth_token_object = self.get_response(auth_)

        return auth_

    def is_authenticated(self):
        if isinstance(self.auth_token_object, dict) and self.auth_token_object.get(
            "access_token", None
        ):
            return True
        return False

    def get_access_token(self):
        if self.is_authenticated():
            return self.auth_token_object["access_token"]

    def get_token_type(self):
        if self.is_authenticated():
            return self.auth_token_object["token_type"]

    def customer_lookup(self, bank_slug, customer_id=None, account_number=None):
        url = iHela_ENDPOINTS["LOOKUP"] % bank_slug
        query_param = account_number or customer_id
        customer_info_ = requests.get(
            self.get_url(url),
            params={"account_number": query_param},
            headers=self.get_auth_headers(),
            timeout=15.0,
        )
        customer_info = self.get_response(customer_info_)

        return customer_info

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
    ):
        if self.is_authenticated():
            debit_account = user
            debit_bank = bank
            bill_data = {
                "debit_bank": debit_bank,
                "debit_account": debit_account,
                "amount": amount,
                "description": description,
                "merchant_description": merchant_description or description,
                "merchant_reference": reference,
                "redirect_uri": redirect_uri,
                "payment_product_id": payment_product_id,
                "pin_code": pin_code,
            }
            bill_data = {k: v for k, v in bill_data.items() if v is not None}
            url = iHela_ENDPOINTS["BILL_INIT"]
            bill_ = requests.post(
                self.get_url(url),
                json=bill_data,
                headers=self.get_auth_headers(),
                timeout=15.0,
            )
            bill_initiated = self.get_response(bill_)

            return bill_initiated
        else:
            return {"errors": {"authentication": "The client is not authenticated"}}

    def verify_bill(self, bill_code: str, merchant_reference: str, pin_code: str):
        bill_data = {
            "bill_code": bill_code,
            "merchant_reference": merchant_reference,
            "pin_code": pin_code,
        }
        url = iHela_ENDPOINTS["BILL_VERIFY"]
        bill_ = requests.post(
            self.get_url(url),
            json=bill_data,
            headers=self.get_auth_headers(),
            timeout=15.0,
        )
        bill_verified = self.get_response(bill_)

        return bill_verified

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
    ):
        if self.is_authenticated():
            cashin_data = {
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
            url = iHela_ENDPOINTS["CASHIN"]
            cashin_ = requests.post(
                self.get_url(url),
                json=cashin_data,
                headers=self.get_auth_headers(),
                timeout=15.0,
            )
            cashin = self.get_response(cashin_)

            return cashin
        else:
            return {"errors": {"authentication": "The client is not authenticated"}}

    def get_bank_list(self):
        if self.is_authenticated():
            url = iHela_ENDPOINTS["BANKS_ALL"]
            banks_ = requests.get(
                self.get_url(url), headers=self.get_auth_headers(), timeout=15.0
            )
            banks = self.get_response(banks_)

            return banks
        else:
            return {"errors": {"authentication": "The client is not authenticated"}}

    def get_cashin_bank_list(self):
        if self.is_authenticated():
            url = iHela_ENDPOINTS["BANKS_CASHIN"]
            banks_ = requests.get(
                self.get_url(url), headers=self.get_auth_headers(), timeout=15.0
            )
            banks = self.get_response(banks_)

            return banks
        else:
            return {"errors": {"authentication": "The client is not authenticated"}}

    def get_cashout_bank_list(self):
        if self.is_authenticated():
            url = iHela_ENDPOINTS["BANKS_CASHOUT"]
            banks_ = requests.get(
                self.get_url(url), headers=self.get_auth_headers(), timeout=15.0
            )
            banks = self.get_response(banks_)

            return banks
        else:
            return {"errors": {"authentication": "The client is not authenticated"}}


if __name__ == "__main__":
    import os

    client_id = os.environ.get("IHELA_CLIENT_ID", "YOUR_CLIENT_ID")
    client_secret = os.environ.get("IHELA_CLIENT_SECRET", "YOUR_CLIENT_SECRET")

    cl = MerchantClient(
        client_id, client_secret
    )  # , ihela_url="http://127.0.0.1:8080/")
    print("\nBILL INIT : ", cl.ihela_base_url)

    bill = cl.init_bill(
        2000,
        # "76077736",
        "pierreclaverkoko@gmail.com",
        "My description",
        str(secrets.token_hex(10)),
        # bank="MOB-0003"
    )
    print(bill)

    if bill["bill"].get("merchant_reference"):
        bill_verif = cl.verify_bill(
            bill["bill"]["code"], bill["bill"]["merchant_reference"], "1234"
        )

        print("\nBILL VERIFY : ", bill_verif)

    banks = cl.get_bank_list()

    print("\nBANKS : ", banks)

    client = cl.customer_lookup("MF1-0001", "000016-01")

    print("\nCLIENT : ", client)

    cashin = cl.cashin_client(
        "MF1-0001", "000016-01", 20000, str(secrets.token_hex(10)), "Cashin description"
    )

    print("\nCASHIN : ", cashin)

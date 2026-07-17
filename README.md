# iHela SDK

[![PyPI version](https://img.shields.io/pypi/v/ihela-sdk)](https://pypi.org/project/ihela-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/ihela-sdk)](https://pypi.org/project/ihela-sdk/)
[![License](https://img.shields.io/pypi/l/ihela-sdk)](https://github.com/UbuhingaVizion/ihela-sdk/blob/develop/LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://UbuhingaVizion.github.io/ihela-sdk/)

Python SDK for the iHela Credit Union API for financial services in Burundi.
Framework-agnostic — works with Django, Flask, FastAPI, or any Python application.

## Installation

```bash
pip install ihela-sdk
```

Or with `uv`:

```bash
uv add ihela-sdk
```

## Quick Start

```python
from ihela_sdk import MerchantClient

client = MerchantClient("your_client_id", "your_client_secret", prod=False)
```

For async applications (FastAPI, asyncio):

```python
from ihela_sdk import AsyncMerchantClient

client = AsyncMerchantClient("your_client_id", "your_client_secret", prod=False)
```

## OAuth2 SSO

```python
from ihela_sdk import MerchantAuthorizationClient

auth = MerchantAuthorizationClient("client_id", "client_secret", prod=False)
login_url = auth.get_authorization_url(redirect_uri="https://app.com/callback/")
# Redirect user to login_url, handle callback with auth.authenticate(code, redirect_uri)
```

See the **[Authentication](https://UbuhingaVizion.github.io/ihela-sdk/authentication/)** guide for Django, Flask, and FastAPI examples.

## Exception Handling

```python
from ihela_sdk import iHelaError, iHelaAPIError, iHelaAuthenticationError

try:
    bill = client.init_bill(2000, "client@example.com", "Payment", "ref-001")
except iHelaAuthenticationError:
    print("Authentication failed. Check your credentials.")
except iHelaAPIError as e:
    print(f"API error (HTTP {e.status_code})")
except iHelaError:
    print("A client error occurred.")
```

## Features

- **Merchant Services**: Bill init/verify, cash-in, bank lists, customer lookup
- **Banking Services**: Deposits, withdrawals, account lookup/balance, statements, transaction fees
- **Agent Services**: Operations, withdrawal validation
- **OAuth2**: Client credentials and authorization code flows
- **Framework-Agnostic**: No web framework dependency — OAuth2 primitives work everywhere
- **Async Support**: Full async client variants using httpx

## Documentation

Full documentation at [UbuhingaVizion.github.io/ihela-sdk](https://UbuhingaVizion.github.io/ihela-sdk/).

## License

MIT — see [LICENSE](LICENSE).

# iHela SDK

[![PyPI version](https://img.shields.io/pypi/v/ihela-sdk)](https://pypi.org/project/ihela-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/ihela-sdk)](https://pypi.org/project/ihela-sdk/)
[![License](https://img.shields.io/pypi/l/ihela-sdk)](https://github.com/UbuhingaVizion/ihela-sdk/blob/develop/LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://UbuhingaVizion.github.io/ihela-sdk/)

Python SDK for the iHela Credit Union API for financial services in Burundi.

## Installation

```bash
pip install ihela-sdk
```

With Django integration:

```bash
pip install "ihela-sdk[django]"
```

Or with `uv`:

```bash
uv add ihela-sdk
# with django extra
uv add "ihela-sdk[django]"
```

## Quick Start

```python
from ihela_sdk import MerchantClient

client = MerchantClient("your_client_id", "your_client_secret", prod=False)
```

For async applications (FastAPI, async Django):

```python
from ihela_sdk import AsyncMerchantClient

client = AsyncMerchantClient("your_client_id", "your_client_secret", prod=False)
```

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
- **Django Integration**: Pre-built views for django-allauth
- **Async Support**: Full async client variants using httpx

## Documentation

Full documentation at [UbuhingaVizion.github.io/ihela-sdk](https://UbuhingaVizion.github.io/ihela-sdk/).

## License

MIT — see [LICENSE](LICENSE).

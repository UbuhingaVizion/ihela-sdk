# Getting Started

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
uv add "ihela-sdk[django]"
```

**Requirements**: Python 3.10+

**Dependencies**: `httpx` (HTTP client), `pydantic` (validation)

---

## Authentication

All clients authenticate automatically using OAuth2 client credentials. Provide
your `client_id` and `client_secret` obtained from iHela.

### Merchant Services

```python
from ihela_sdk import MerchantClient

client = MerchantClient("your_client_id", "your_client_secret", prod=False)
```

### Banking Services

```python
from ihela_sdk import BankingClient

client = BankingClient("your_client_id", "your_client_secret", prod=False)
```

### Agent Services

```python
from ihela_sdk import AgentClient

client = AgentClient("your_client_id", "your_client_secret", prod=False)
```

Set `prod=True` for the production environment. The default (`False`) uses the
test gateway at `https://testgate.ihela.online/`.

---

## Environment URLs

| Environment | Gateway URL |
|-------------|-------------|
| Test | `https://testgate.ihela.online/` |
| Production | `https://gate.ihela.online/` |

Override with a custom URL via the `ihela_url` parameter on any client.

---

## Quick Example

```python
from ihela_sdk import MerchantClient

client = MerchantClient("your_client_id", "your_client_secret")
bill = client.init_bill(
    amount=2000,
    user="customer@example.com",
    description="Invoice #123",
    reference="merchant-ref-001",
    pin_code="1234",
)

status = client.verify_bill(
    bill_code=bill["bill"]["code"],
    merchant_reference=bill["bill"]["merchant_reference"],
    pin_code="1234",
)
```

---

## Error Handling

The SDK raises structured exceptions on failures:

```python
from ihela_sdk import (
    iHelaError,
    iHelaAuthenticationError,
    iHelaAPIError,
)

try:
    result = client.ping()
except iHelaAuthenticationError:
    print("Invalid credentials or connection refused.")
except iHelaAPIError as e:
    print(f"Gateway error (HTTP {e.status_code})")
except iHelaError:
    print("General client error.")
```

- **`iHelaAuthenticationError`** — Raised when authentication fails or the
  gateway is unreachable.
- **`iHelaAPIError`** — Raised on invalid inputs or gateway errors. The message
  is intentionally generic to prevent information leakage.

---

## Async Usage

All clients have async counterparts. Use them in `asyncio` applications:

```python
from ihela_sdk import AsyncBankingClient

client = AsyncBankingClient("client_id", "client_secret")

balance = await client.account_balance("76077736")
deposit = await client.deposit(
    credit_account="ACT-123",
    credit_account_holder="John Doe",
    amount=500.0,
    description="Invoice payment",
    external_reference="REF-001",
    pin_code="1234",
)
```

---

## Next Steps

* See the **[API Reference](api.md)** for all available methods and schemas.
* See **[Django Integration](django.md)** for setting up OAuth2 with django-allauth.

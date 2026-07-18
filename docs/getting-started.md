# Getting Started

## Installation

```bash
pip install ihela-sdk
```

Or with `uv`:

```bash
uv add ihela-sdk
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

## Security

### Credential Protection

The SDK never logs client credentials or access tokens. All sensitive fields
(`pin_code`, `access_token`, `client_secret`, `password`, etc.) in API responses
are automatically masked with `********` before debug logging.

Client objects have a safe `__repr__` that only shows the environment flag:

```python
>>> client
<BankingClient prod_env=False>   # no credentials exposed
```

### Token Injection

Skip authentication entirely by passing a pre-obtained token — no credentials
are stored or transmitted:

```python
client = BankingClient("client_id", "client_secret",
    token={"access_token": "...", "token_type": "Bearer"})
```

Or defer authentication to the first API call:

```python
client = BankingClient("client_id", "client_secret", auto_auth=False)
# Token is acquired only when needed
balance = client.account_balance("76077736")
```

### Token Lifecycle

Clear a token from memory after use:

```python
client.clear_token()
```

### Request Signing

For Banking and Agent clients, provide a `signature_key` to HMAC-SHA256 sign
every deposit and withdrawal request:

```python
client = BankingClient("id", "secret", signature_key="your-signing-key")
client.deposit(...)
# Automatically adds X-iHela-Signature header
```

For incoming webhooks or callbacks, verify signatures received from iHela:

```python
from ihela_sdk import verify_signature

is_valid = verify_signature(payload, signature, secret_key)
```

### Error Handling Philosophy

The SDK raises a single generic `iHelaAPIError` for all gateway failures.
The message is intentionally non-specific to prevent bots from mapping your
environment (which accounts exist, which operations are live). Use the
`response_code` attribute for internal programmatic handling only:

```python
try:
    client.deposit(...)
except iHelaAPIError as e:
    # Never show response_code to end users
    logger.warning(f"Deposit failed with code {e.response_code}")

    if e.is_retryable:
        await retry_later(...)  # Transient failures (5xx, code "07")

    return {"error": "Transaction could not be completed"}
```

---

## Production Guardrails

### Circuit Breaker

Prevents cascading failures when the iHela gateway is down. After 5 consecutive
failures, all calls are suspended for 30 seconds:

```python
client = BankingClient("id", "secret",
    circuit_breaker_threshold=5,     # failures before opening
    circuit_breaker_cooldown=30.0,   # seconds before retry
)

try:
    client.ping()
except iHelaCircuitOpenError:
    print("Gateway is down — circuit breaker open")
```

### Rate Limiting

Prevent self-DoS with a token bucket per client instance:

```python
client = BankingClient("id", "secret", rate_limit=100)  # 100 req/min

try:
    client.deposit(...)
except iHelaRateLimitError:
    print("Too many requests — slow down")
```

### Idempotency

On deposit and withdrawal operations, if no `external_reference` is provided,
the SDK auto-generates a UUID to prevent duplicate transactions:

```python
# Automatically gets a UUID external_reference
client.deposit(credit_account="ACT-123", credit_account_holder="John",
               amount=500.0, description="Payment", pin_code="1234")

# Or provide your own for idempotency across retries
client.deposit(credit_account="ACT-123", credit_account_holder="John",
               amount=500.0, description="Payment", pin_code="1234",
               external_reference="my-unique-ref-001")
```

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
* See **[Authentication](authentication.md)** for OAuth2 and SSO setup.

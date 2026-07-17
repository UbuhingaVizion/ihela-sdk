# API Reference

## MerchantClient

Handles payments, bills, bank lists, and customer lookups.

```python
from ihela_sdk import MerchantClient

client = MerchantClient("client_id", "client_secret", prod=False)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client_id` | `str` | required | OAuth2 client ID from iHela |
| `client_secret` | `str` | required | OAuth2 client secret |
| `prod` | `bool` | `False` | `True` for production, `False` for test gateway |
| `ihela_url` | `str` | `None` | Override the base gateway URL |

---

### `customer_lookup(bank_slug, customer_id=None, account_number=None)`

Look up a customer account by bank slug and account number or customer ID.

```python
customer = client.customer_lookup(bank_slug="MF1-0001", account_number="76000111")
# {'account_number': '000001-01', 'name': 'Bigirimana Fabrice', 'response_status': 200}
```

---

### `init_bill(amount, user, description, reference, *, bank=None, bank_client_id=None, redirect_uri=None, pin_code=None, merchant_description=None, payment_product_id=None)`

Create a payment bill. The user must confirm payment in iHela.

| Parameter | Type | Description |
|-----------|------|-------------|
| `amount` | `int` | Amount in BIF |
| `user` | `str` | Customer email, phone, or iHela ID |
| `description` | `str` | Payment description |
| `reference` | `str` | Unique merchant reference |
| `bank` | `str \| None` | Bank slug (e.g. `"MF1-0001"`) |
| `pin_code` | `str \| None` | 4-digit pin |
| `redirect_uri` | `str \| None` | Redirect URL after payment |

```python
bill = client.init_bill(
    amount=600,
    user="76000111",
    description="Product Purchase",
    reference="merchant-ref-001",
    bank="MF1-0001",
    redirect_uri="https://yourapp.com/callback/",
    pin_code="1234",
)
# {'bill': {'code': 'CODE-20230321-9E29QH1', ...}, 'response_status': 200}
```

---

### `verify_bill(bill_code, merchant_reference, pin_code)`

Check if a bill has been paid, is pending, expired, or cancelled.

```python
status = client.verify_bill(
    bill_code="CODE-20230321-9E29QH1",
    merchant_reference="merchant-ref-001",
    pin_code="1234",
)
# response_data.status can be: "Initial", "Paid", "Canceled", or "Error"
```

---

### `cashin_client(bank_slug, account, amount, merchant_reference, description, *, pin_code=None, credit_account_holder=None, currency="BIF")`

Send money or refund a customer account.

```python
cashin = client.cashin_client(
    bank_slug="MF1-0001",
    account="000001-01",
    amount=20000,
    merchant_reference="REF3223",
    description="Refunding customer",
    pin_code="1234",
)
```

---

### `get_bank_list()`

Returns all available payment banks.

```python
banks = client.get_bank_list()
# {'banks': [{'slug': 'MF1-0001', 'name': 'iHela Credit Union', ...}], ...}
```

---

### `get_cashin_bank_list()` / `get_cashout_bank_list()`

Returns banks supporting cash-in or cash-out operations.

---

### Properties

| Method | Description |
|--------|-------------|
| `get_access_token()` | Returns the current access token |
| `is_authenticated()` | Whether the client has a valid token |

---

## BankingClient

Banking operations: deposits, withdrawals, account management, and transactions.

```python
from ihela_sdk import BankingClient

client = BankingClient("client_id", "client_secret", prod=False)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client_id` | `str` | required | OAuth2 client ID |
| `client_secret` | `str` | required | OAuth2 client secret |
| `prod` | `bool` | `False` | Environment selector |
| `ihela_url` | `str` | `None` | Override base URL |
| `ssl_cert` | `any` | `None` | SSL client certificate path |
| `signature_key` | `str` | `None` | HMAC signing key for `X-iHela-Signature` header |

---

### `ping()`

Health check — verifies connectivity and authentication.

```python
client.ping()
# {'success': True, 'response_status': 200}
```

---

### `request_token(username, password)`

Request tokens via username/password (alternative to client credentials).

```python
tokens = client.request_token("username", "password")
# {'access': '...', 'refresh': '...'}
```

---

### `account_lookup(account_number)`

Retrieve account details by account number.

```python
info = client.account_lookup("76077736")
```

---

### `account_balance(account_number)`

Get the current balance for an account.

```python
balance = client.account_balance("76077736")
```

---

### `deposit(credit_account, credit_account_holder, amount, description, external_reference, pin_code, external_code="")`

Deposit funds into an account. Payload is validated with `DepositPayload`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `credit_account` | `str` | Target account number |
| `credit_account_holder` | `str` | Account holder name |
| `amount` | `float` | Positive amount |
| `description` | `str` | Transaction description |
| `external_reference` | `str` | Your unique reference |
| `pin_code` | `str` | 4-6 digit pin |
| `external_code` | `str` | Optional external code |

```python
client.deposit(
    credit_account="ACT-123",
    credit_account_holder="John Doe",
    amount=500.0,
    description="Invoice #42",
    external_reference="REF-001",
    pin_code="1234",
)
```

---

### `withdrawal(debit_account, debit_account_holder, amount, description, external_reference, pin_code)`

Withdraw funds from an account. Payload is validated with `WithdrawalPayload`.

```python
client.withdrawal(
    debit_account="ACT-123",
    debit_account_holder="John Doe",
    amount=1000.0,
    description="Cash withdrawal",
    external_reference="REF-002",
    pin_code="1234",
)
```

---

### `statement(account_number)`

Get a mini-statement for an account.

```python
stmt = client.statement("76077736")
```

---

### `transaction_status(external_reference, reference)`

Check the status of a transaction.

```python
status = client.transaction_status("REF-001", "internal-reference")
```

---

### `transaction_fee(currency, operation_type, amount)`

Query transaction fees before performing an operation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `currency` | `str` | ISO currency code (e.g. `"BIF"`) |
| `operation_type` | `str` | `"deposit"`, `"withdrawal"`, etc. |
| `amount` | `str` | Amount to query |

```python
fee = client.transaction_fee("BIF", "withdrawal", "4000")
# {'success': True, 'response_data': {'fee': '100', 'currency': 'BIF', ...}}
```

---

### Token Management

| Method | Description |
|--------|-------------|
| `authenticate()` | Acquire a new access token |
| `refresh_token()` | Refresh an expired access token |
| `is_authenticated()` | Check if token is valid |

---

## AgentClient

Agent-specific operations: deposits and withdrawal validation.

```python
from ihela_sdk import AgentClient

client = AgentClient("client_id", "client_secret", prod=False)
```

Same constructor parameters as `BankingClient`.

---

### `ping()`

Health check.

### `request_token(username, password)`

Username/password token request.

### `account_lookup(account_number)` / `account_balance(account_number)`

Same as BankingClient.

---

### `deposit(credit_account, credit_account_holder, amount, description, external_reference, pin_code, external_code="")`

Agent deposit. Validated with `DepositPayload`. Hits `agent-deposit/` endpoint.

---

### `operation_lookup(operation_code, amount)`

Look up an operation by its code.

```python
result = client.operation_lookup("op-code", "5000")
# {'validation_operation_code': 'val-123', ...}
```

---

### `validate_withdrawal(external_reference, pin_code, agent_code, amount, external_code, validation_operation_code)`

Validate and confirm a withdrawal. Validated with `ValidateWithdrawalPayload`.

```python
client.validate_withdrawal(
    external_reference="REF-123",
    pin_code="1234",
    agent_code="AGT-001",
    amount="5000",
    external_code="EXT-001",
    validation_operation_code="VAL-001",
)
```

---

### `transaction_status(external_reference, reference)`

Same as BankingClient.

---

## Async Clients

Every client has an async counterpart. Import from `ihela_sdk`:

| Sync | Async |
|------|-------|
| `MerchantClient` | `AsyncMerchantClient` |
| `BankingClient` | `AsyncBankingClient` |
| `AgentClient` | `AsyncAgentClient` |

```python
from ihela_sdk import AsyncBankingClient

async def main():
    client = AsyncBankingClient("id", "secret")
    await client.authenticate()
    balance = await client.account_balance("76077736")
```

All methods are identical — just `await` them.

---

## Pydantic Models

The SDK exports validation models you can use directly:

```python
from ihela_sdk import DepositPayload, WithdrawalPayload, ValidateWithdrawalPayload

# Validate before calling the API
payload = DepositPayload(
    credit_account="ACT-1234",
    credit_account_holder="John Doe",
    amount=1500.50,
    description="Invoice Payment",
    external_reference="REF-883",
    pin_code="1234",
)
```

### `DepositPayload`

| Field | Type | Constraints |
|-------|------|-------------|
| `credit_account` | `str` | 3-50 chars, `[A-Z0-9\-]` |
| `credit_account_holder` | `str` | 2-100 chars |
| `amount` | `float` | `> 0` |
| `description` | `str` | 1-255 chars |
| `external_reference` | `str` | 3-100 chars |
| `pin_code` | `str` | 4-6 digits |
| `external_code` | `str` | Optional, max 100 chars |

### `WithdrawalPayload`

| Field | Type | Constraints |
|-------|------|-------------|
| `debit_account` | `str` | 3-50 chars, `[A-Z0-9\-]` |
| `debit_account_holder` | `str` | 2-100 chars |
| `amount` | `float` | `> 0` |
| `description` | `str` | 1-255 chars |
| `external_reference` | `str` | 3-100 chars |
| `pin_code` | `str` | 4-6 digits |

---

## Security

### Sensitive Data Masking

All API responses are automatically scanned before debug logging. The following
fields are replaced with `********`:

`pin_code`, `access_token`, `refresh_token`, `client_secret`, `client_id`,
`password`, `token`, `secret`, `api_key`, `authorization`

### Safe Object Representation

`__repr__` never exposes credentials — it only shows the class name and
environment flag:

```python
>>> client
<BankingClient prod_env=False>
```

### Token Lifecycle

All clients support `clear_token()` to remove the access token from memory:

```python
client.clear_token()  # auth_token_object is now None
```

### Token Injection

Pass a pre-obtained token to skip authentication — no credentials are
transmitted:

```python
client = BankingClient("id", "secret",
    token={"access_token": "...", "token_type": "Bearer"})

client = BankingClient("id", "secret", auto_auth=False)
# Authenticates lazily on the first API call
```

### Request Signing

Provide a `signature_key` to Banking or Agent clients to HMAC-SHA256 sign
every deposit, withdrawal, and validation request:

```python
client = BankingClient("id", "secret", signature_key="your-key")
client.deposit(...)
# Adds X-iHela-Signature: <hmac-sha256-hex> header
```

---

## Endpoint Reference

The SDK maps to the following iHela API endpoints:

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `oAuth2/token/` | Obtain access token (client credentials) |
| POST | `ihela/api/v1/auth-token/` | Obtain token via username/password |
| POST | `ihela/api/v1/auth-token/refresh/` | Refresh access token |

### Merchant Services

| Method | Path | Description |
|--------|------|-------------|
| GET | `api/v1/payments/bank/` | List all banks |
| GET | `api/v1/payments/bank/cashin/` | List cash-in banks |
| GET | `api/v1/payments/bank/cashout/` | List cash-out banks |
| GET | `api/v1/bank/{slug}/account/lookup/` | Customer account lookup |
| POST | `api/v1/payments/bill-init/` | Initialize a bill |
| POST | `api/v1/payments/bill-check/` | Verify bill status |
| POST | `api/v1/payments/cash-in/` | Cash-in to customer account |

### Banking Services

| Method | Path | Description |
|--------|------|-------------|
| GET | `ihela/api/v1/ping/` | Health check |
| POST | `ihela/api/v1/account-lookup/` | Account lookup |
| POST | `ihela/api/v1/bsces/balance/` | Account balance |
| POST | `ihela/api/v1/make-deposit/` | Deposit funds |
| POST | `ihela/api/v1/make-withdrawal/` | Withdraw funds |
| GET | `ihela/api/v1/mini-statement/` | Mini statement |
| POST | `ihela/api/v1/transaction-status/` | Transaction status |
| POST | `ihela/api/v1/transaction-fee/` | Transaction fee query |

### Agent Services

| Method | Path | Description |
|--------|------|-------------|
| GET | `ihela/api/v1/ping/` | Health check |
| POST | `ihela/api/v1/account-lookup/` | Account lookup |
| POST | `ihela/api/v1/bsces/balance/` | Account balance |
| POST | `ihela/api/v1/agent-deposit/` | Agent deposit |
| POST | `ihela/api/v1/operation-lookup/` | Operation lookup |
| POST | `ihela/api/v1/validate-withdrawal/` | Validate withdrawal |
| POST | `ihela/api/v1/transaction-status/` | Transaction status |

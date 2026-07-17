# API Reference

## MerchantClient

The `MerchantClient` handles direct integration with payment banks, lookup queries, and billing endpoints.

### Querying Banks

Retrieve the list of payment banks accepting payments:

```python
# Cashin banks (e.g. ICU, EcoCash, PesaFlash)
cashin_banks = client.get_cashin_bank_list()

# Cashout banks
cashout_banks = client.get_cashout_bank_list()
```

---

### Account Lookup

Verify a customer's account details before initiating a payment:

```python
customer_info = client.customer_lookup(
    bank_slug="MOB-0003",
    account_number="76000111"
)
# Returns {'account_number': '000001-01', 'name': 'Bigirimana Fabrice', 'response_status': 200}
```

---

### Initialize Bill

Generate a billing operation to redirect users for payment confirmation:

```python
bill = client.init_bill(
    amount=2000,
    user="76000111",  # customer email, phone, or ihela id
    description="Product Purchase",
    reference="unique_merchant_ref",
    redirect_uri="https://yourapp.com/payment/callback/",
    pin_code="1234",
)
```

---

### Verify Bill

Check if a bill has been paid or if it has expired:

```python
status = client.verify_bill(
    bill_code=bill["bill"]["code"],
    merchant_reference=bill["bill"]["merchant_reference"],
    pin_code="1234",
)
```

---

### Account Cashin

Send money or refund a customer account:

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

## BankingClient

The `BankingClient` handles banking operations: deposits, withdrawals, account lookups, and statements.

```python
from ihela_sdk import BankingClient

client = BankingClient("your_client_id", "your_client_secret", prod=False)
```

### Deposit

```python
client.deposit(
    credit_account="ACT-123",
    credit_account_holder="John Doe",
    amount=500.0,
    description="Invoice payment",
    external_reference="REF-001",
    pin_code="1234",
)
```

### Withdrawal

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

### Account Lookup & Balance

```python
lookup = client.account_lookup("76077736")
balance = client.account_balance("76077736")
```

### Transaction Status & Fees

```python
status = client.transaction_status("REF-001", "internal-ref")
fee = client.transaction_fee("BIF", "withdrawal", "4000")
```

---

## AgentClient

The `AgentClient` handles agent-specific operations for validating withdrawals and deposits.

```python
from ihela_sdk import AgentClient

client = AgentClient("your_client_id", "your_client_secret", prod=False)
```

### Deposit

```python
client.deposit(
    credit_account="ACT-123",
    credit_account_holder="John Doe",
    amount=500.0,
    description="Agent deposit",
    external_reference="REF-001",
    pin_code="1234",
)
```

### Validate Withdrawal

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

## Async Variants

All clients have async counterparts for use with `asyncio`:

```python
from ihela_sdk import AsyncMerchantClient, AsyncBankingClient, AsyncAgentClient

client = AsyncMerchantClient("client_id", "client_secret", prod=False)
result = await client.init_bill(
    amount=2000,
    user="user@example.com",
    description="Payment",
    reference="ref-001",
)
```

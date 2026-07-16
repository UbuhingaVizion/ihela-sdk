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
    user="76000111", # customer email, phone, or ihela id
    description="Product Purchase",
    reference="unique_merchant_ref",
    redirect_uri="https://yourapp.com/payment/callback/"
)
```

---

### Verify Bill
Check if a bill has been paid or if it has expired:

```python
status = client.verify_bill(
    code=bill["bill"]["code"],
    reference=bill["bill"]["merchant_reference"]
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
    description="Refunding customer"
)
```

# iHela SDK

Python SDK for the **[iHela Credit Union API](https://bankingdocs.ihela.bi/)** — a
financial services platform for banking, payments, and mobile money in Burundi.

This library provides typed, authenticated access to all iHela services with both
synchronous and asynchronous clients backed by `httpx`.

---

## Key Features

* **Merchant Services** — Initiate and verify bills, cash-in to customer accounts,
  query bank lists, and perform customer lookups.
* **Banking Services** — Deposits, withdrawals, account lookups, balance checks,
  mini-statements, transaction status, and fee calculation.
* **Agent Services** — Agent deposits, withdrawal validation, and operation lookups.
* **OAuth2 Authentication** — `client_credentials` and `authorization_code` grant
  flows with automatic token refresh.
* **Django Integration** — Pre-built views for `django-allauth` OAuth2 flows.
* **Async & Sync** — Identical API surface via `BankingClient` / `AsyncBankingClient`,
  `AgentClient` / `AsyncAgentClient`, and `MerchantClient` / `AsyncMerchantClient`.
* **Type-Checked** — PEP 561 `py.typed` marker and full type annotations.
* **Input Validation** — Pydantic models validate deposit, withdrawal, and
  validation payloads before they reach the gateway.
* **Security** — HMAC-SHA256 request signing, sensitive field masking in debug logs.

---

## Navigation

* **[Getting Started](getting-started.md)** — Install, authenticate, and make your first call.
* **[API Reference](api.md)** — Complete reference for all clients, methods, and schemas.
* **[Django Integration](django.md)** — Set up OAuth2 views with django-allauth.

---

## Related Links

* [iHela Official Documentation](https://bankingdocs.ihela.bi/)
* [GitHub Repository](https://github.com/UbuhingaVizion/ihela-sdk)
* [PyPI Package](https://pypi.org/project/ihela-sdk/)

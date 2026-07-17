# iHela SDK

Python SDK for the **[iHela Credit Union API](https://bankingdocs.ihela.bi/)** — a
financial services platform for banking, payments, and mobile money in Burundi.

This library provides typed, authenticated access to all iHela services with both
synchronous and asynchronous clients backed by `httpx`.

---

## Key Features

* **OAuth2 Authentication** — `client_credentials` and `authorization_code` grant
  flows with automatic token refresh. Inject pre-obtained tokens or defer auth.
* **Merchant Services** — Initiate and verify bills, cash-in to customer accounts,
  query bank lists, and perform customer lookups.
* **Banking Services** — Deposits, withdrawals, account lookups, balance checks,
  mini-statements, transaction status, and fee calculation.
* **Agent Services** — Agent deposits, withdrawal validation, and operation lookups.
* **Framework-Agnostic** — No web framework dependency. OAuth2 primitives work
  with Django, Flask, FastAPI, or any Python application.
* **Async & Sync** — Identical API surface via `BankingClient` / `AsyncBankingClient`,
  `AgentClient` / `AsyncAgentClient`, and `MerchantClient` / `AsyncMerchantClient`.
* **Type-Checked** — PEP 561 `py.typed` marker and full type annotations.
* **Input Validation** — Pydantic models validate deposit, withdrawal, and
  validation payloads before they reach the gateway.
* **Security** — HMAC-SHA256 request signing, sensitive field masking in debug logs,
  credential-safe `__repr__`, explicit token clearing.

---

## Navigation

* **[Getting Started](getting-started.md)** — Install, authenticate, and make your first call.
* **[API Reference](api.md)** — Complete reference for all clients, methods, and schemas.
* **[Authentication](authentication.md)** — OAuth2 flows and framework integration (Django, Flask, FastAPI).

---

## Related Links

* [iHela Official Documentation](https://bankingdocs.ihela.bi/)
* [GitHub Repository](https://github.com/UbuhingaVizion/ihela-sdk)
* [PyPI Package](https://pypi.org/project/ihela-sdk/)

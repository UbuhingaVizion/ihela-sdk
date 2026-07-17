# iHela SDK

Welcome to the documentation for the Python SDK for the **iHela Credit Union API** for financial and payment services in Burundi.

This library simplifies integrating bank payments, mobile money cash-ins, and bill settlements within Burundian financial networks.

---

## Key Features

* **OAuth2 Authentication**: Integrated support for both `client_credentials` and `authorization_code` OAuth2 grant flows.
* **Payment Initialization & Verification**: Initialize bills and securely check their status.
* **Bank lists & Lookup**: Query active cash-in/cash-out bank channels and perform account lookup checks.
* **Banking & Agent Services**: Deposits, withdrawals, account lookups, transaction fees, and more.
* **Django Integration**: Pre-built base views for seamless integration with Django and `django-allauth`.
* **Async Support**: Full async client variants using `httpx`.
* **Modernized Tooling**: Optimized with `uv`, `ruff`, and standard PEP 621 layouts.

---

## Navigation

* **[Getting Started](getting-started.md)**: Install the client and initialize your first session.
* **[API Reference](api.md)**: Explore client endpoints, parameters, and methods.
* **[Django Integration](django.md)**: Set up single sign-on and OAuth redirect handlers.

# Getting Started

## Installation

You can install the package directly using `pip`:

```bash
pip install ihela-python-client
```

If you are using Django, you can install the library with the optional `django` dependencies:

```bash
pip install "ihela-python-client[django]"
```

Or using `uv`:

```bash
uv add ihela-python-client
# with django extra
uv add "ihela-python-client[django]"
```

---

## Getting a Client Instance

To communicate with the iHela API, initialize a `MerchantClient` instance with your credentials:

```python
from ihela_client import MerchantClient

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
PROD_ENV = False  # Set to True for production environment

client = MerchantClient(CLIENT_ID, CLIENT_SECRET, prod=PROD_ENV)
```

The client will automatically authenticate and acquire a token on initialization.

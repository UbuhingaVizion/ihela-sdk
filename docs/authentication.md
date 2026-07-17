# Authentication

The SDK is **framework-agnostic** — it doesn't depend on Django, Flask, FastAPI,
or any specific web framework. You manage routes, sessions, and token storage
in your application, and the SDK provides the OAuth2 primitives.

---

## Client Credentials (Machine-to-Machine)

For backend services that authenticate without a user:

```python
from ihela_sdk import BankingClient

client = BankingClient("your_client_id", "your_client_secret")
# Authenticates automatically on init
```

---

## Authorization Code (User-to-Machine / SSO)

For web applications where a user signs in through iHela:

### 1. Redirect the user to iHela

```python
from ihela_sdk import MerchantAuthorizationClient

auth = MerchantAuthorizationClient(
    "your_client_id", "your_client_secret",
    prod=False,  # True for production
)

login_url = auth.get_authorization_url(
    redirect_uri="https://yourapp.com/callback/"
)
# Redirect user to login_url
```

### 2. Handle the callback

```python
# In your callback route handler:
code = request.GET.get("code")  # or request.args.get("code") in Flask

auth.authenticate(code, redirect_uri="https://yourapp.com/callback/")
user = auth.get_user_info()

# Store the token in your session:
session["ihela_token"] = {
    "access_token": auth.get_access_token(),
    "token_type": auth.get_token_type(),
}
```

### 3. Use the token on subsequent requests

```python
client = BankingClient(
    "your_client_id", "your_client_secret",
    token=session["ihela_token"],
)
balance = client.account_balance("76077736")
```

---

## Framework Examples

### Django

```python
# urls.py
urlpatterns = [
    path("ihela/login/", views.ihela_login, name="ihela-login"),
    path("ihela/callback/", views.ihela_callback, name="ihela-callback"),
]


# views.py
def ihela_login(request):
    auth = MerchantAuthorizationClient(
        settings.IHELA_CLIENT_ID, settings.IHELA_CLIENT_SECRET,
        prod=not settings.IHELA_TEST_ENV,
    )
    url = auth.get_authorization_url(
        redirect_uri=request.build_absolute_uri("/ihela/callback/")
    )
    return redirect(url)


def ihela_callback(request):
    code = request.GET["code"]
    auth = MerchantAuthorizationClient(
        settings.IHELA_CLIENT_ID, settings.IHELA_CLIENT_SECRET,
        prod=not settings.IHELA_TEST_ENV,
    )
    auth.authenticate(code, redirect_uri=request.build_absolute_uri("/ihela/callback/"))
    request.session["ihela_token"] = {
        "access_token": auth.get_access_token(),
        "token_type": auth.get_token_type(),
    }
    return redirect("/dashboard")
```

### Flask

```python
@app.route("/ihela/login")
def ihela_login():
    auth = MerchantAuthorizationClient(
        app.config["IHELA_CLIENT_ID"], app.config["IHELA_CLIENT_SECRET"],
        prod=False,
    )
    url = auth.get_authorization_url(redirect_uri=url_for("ihela_callback", _external=True))
    return redirect(url)


@app.route("/ihela/callback")
def ihela_callback():
    code = request.args["code"]
    auth = MerchantAuthorizationClient(
        app.config["IHELA_CLIENT_ID"], app.config["IHELA_CLIENT_SECRET"],
        prod=False,
    )
    auth.authenticate(code, redirect_uri=url_for("ihela_callback", _external=True))
    session["ihela_token"] = {
        "access_token": auth.get_access_token(),
        "token_type": auth.get_token_type(),
    }
    return redirect("/dashboard")
```

### FastAPI

```python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

@app.get("/ihela/login")
async def ihela_login(request: Request):
    auth = MerchantAuthorizationClient(
        settings.ihela_client_id, settings.ihela_client_secret, prod=False
    )
    url = auth.get_authorization_url(redirect_uri=str(request.url_for("ihela_callback")))
    return RedirectResponse(url)


@app.get("/ihela/callback")
async def ihela_callback(request: Request, code: str):
    auth = MerchantAuthorizationClient(
        settings.ihela_client_id, settings.ihela_client_secret, prod=False
    )
    auth.authenticate(code, redirect_uri=str(request.url_for("ihela_callback")))
    request.session["ihela_token"] = {
        "access_token": auth.get_access_token(),
        "token_type": auth.get_token_type(),
    }
    return RedirectResponse("/dashboard")
```

---

## Token Injection

Skip authentication entirely by passing a pre-obtained token — useful for load-balanced services or when the token is managed externally:

```python
client = BankingClient("id", "secret",
    token={"access_token": "...", "token_type": "Bearer"})
```

---

## Important Notes

* **Never commit credentials**. Use environment variables or a secrets manager.
* Store tokens in your framework's session mechanism — the SDK does not persist tokens.
* The `MerchantAuthorizationClient` is for user-facing OAuth2 flows only. Use
  `BankingClient` / `AgentClient` / `MerchantClient` for API operations.

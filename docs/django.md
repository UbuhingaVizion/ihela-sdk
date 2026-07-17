# Django Integration

The SDK includes pre-configured Django views that plug into the `django-allauth`
social accounts framework for OAuth2 authorization flows.

---

## Installation

```bash
pip install "ihela-sdk[django]"
```

---

## Configuration

Add to your Django `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'allauth',
    'allauth.socialaccount',
    'ihela_sdk.django',
]

# Test environment (True) or production (False)
IHELA_TEST_ENV = True

# iHela gateway base URL
OAUTH_IHELA_SERVER_BASEURL = "https://testgate.ihela.online"
```

When `IHELA_TEST_ENV = False` (production), the view initializes the client with
`prod=True`, routing requests to `https://gate.ihela.online/`.

---

## Views

Two base views are provided:

* **`iHelaClientBaseView`** — Base OAuth2 view for GET/POST handling with
  authenticated users.
* **`iHelaClientCodeView`** — Extends the base view with `get_code()` and
  `get_error()` helpers.

Extend `iHelaClientCodeView` in your application:

```python
from ihela_sdk.django.views import iHelaClientCodeView


class MyPaymentCallbackView(iHelaClientCodeView):
    """Handle the OAuth2 callback after user authorization."""

    def get_payment_object(self):
        # Retrieve the payment transaction from your database
        # based on the state or reference
        return YourPaymentModel.objects.get(state=self.client.state)
```

`get_payment_object()` must be implemented — it should return the object
representing the payment transaction being processed.

---

## URL Configuration

Wire the view in your `urls.py`:

```python
from django.urls import path
from .views import MyPaymentCallbackView

urlpatterns = [
    path("ihela/callback/", MyPaymentCallbackView.as_view(), name="ihela-callback"),
]
```

Register this callback URL with your iHela client configuration.

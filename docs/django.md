# Django Integration

The client library includes pre-configured Django views that plug into the `django-allauth` social accounts framework to handle user authorization and callback redirect endpoints.

---

## Setup

First, configure your environment settings in your Django `settings.py`:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'allauth',
    'allauth.socialaccount',
    'ihela_sdk.django',  # Register the ihela_sdk django module
]

IHELA_TEST_ENV = True  # True for sandbox, False for production
OAUTH_IHELA_SERVER_BASEURL = "https://testgate.ihela.online"
```

---

## Views

Import the built-in view classes to handle user authentication:

```python
from ihela_sdk.django.views import iHelaClientBaseView, iHelaClientCodeView

# Extend these classes inside your application views to override logic
# and implement get_payment_object():

class MyPaymentCallbackView(iHelaClientCodeView):
    def get_payment_object(self):
        # Implementation to retrieve the payment transaction model
        pass
```

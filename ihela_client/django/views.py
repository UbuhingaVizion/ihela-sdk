from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.oauth2.views import OAuth2View
from django.conf import settings
from django.http import HttpResponseNotAllowed

from ihela_client import MerchantAuthorizationClient as iHelaAPIClient


class iHelaClientBaseView(OAuth2View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.provider = self.adapter.get_provider()
        self.app = self.provider.get_app(self.request)
        self.client = self.get_client(request, self.app)
        self.client.state = SocialLogin.stash_state(request)

        if request.method == "GET":
            return self.get(request, *args, **kwargs)
        elif request.method == "POST":
            return self.post(request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(["GET", "POST"])

    def get_client(self, request, app):
        client_id = getattr(app, "client_id", getattr(app, "consumer_key", None))
        client_secret = getattr(app, "secret", getattr(app, "consumer_secret", None))
        test_env = getattr(settings, "IHELA_TEST_ENV", True)
        ihela_url = (
            getattr(
                settings, "OAUTH_IHELA_SERVER_BASEURL", "https://testgate.ihela.online"
            )
            + "/"
        )
        cl = iHelaAPIClient(
            client_id,
            client_secret,
            state=None,
            test=test_env,
            ihela_url=ihela_url,
        )

        return cl

    @property
    def get_absolute_url(self):
        return self.request.build_absolute_uri(self.request.path)


class iHelaClientCodeView(iHelaClientBaseView):
    def get_code(self):
        return self.request.GET.get("code", None)

    def get_error(self):
        return self.request.GET.get("error", None)

    def get_payment_object(self):
        raise NotImplementedError(
            "An iHelaClientCodeView child must have a method called `get_payment_object`."
        )

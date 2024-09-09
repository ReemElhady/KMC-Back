from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from user.models import User

SMSA_AUTH_TOKEN = "oRxfGY7a7a555nTFSfI5kD"


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        custom_auth_token = request.META.get("HTTP_AUTHORIZATION")
        if not custom_auth_token:
            raise AuthenticationFailed
        if custom_auth_token != SMSA_AUTH_TOKEN:
            raise AuthenticationFailed

        return None

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User


class DefaultTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, token):
        try:
            user = User.objects.get(token=token)
        except ObjectDoesNotExist:
            raise AuthenticationFailed('It is not a valid token.')

        return (user, token)

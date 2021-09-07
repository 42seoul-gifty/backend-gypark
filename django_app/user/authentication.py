from django.conf import settings

from dj_rest_auth.jwt_auth import JWTCookieAuthentication

from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError
)
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework.exceptions import AuthenticationFailed


class CookieAutoRefreshAuthentication(JWTCookieAuthentication):
    def authenticate(self, request):
        cookie_name = getattr(settings, 'JWT_AUTH_COOKIE')
        raw_token = request.COOKIES.get(cookie_name)
        if not raw_token:
            return self.try_refresh(request)

        try:
            token_obj = self.get_validated_token(raw_token)
            return self.get_user(token_obj), token_obj
        except InvalidToken:
            return self.try_refresh(request, raw_token)

    def try_refresh(self, request, access_token=None):
        cookie_name = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', None)
        refresh_token = request.COOKIES.get(cookie_name)

        if not refresh_token and not access_token:
            return None
        if not refresh_token and access_token:
            raise AuthenticationFailed('access_token이 유효하지 않습니다. 다시 로그인 해주세요.')

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            raise AuthenticationFailed('refresh_token이 유효하지 않습니다. 다시 로그인 해주세요.')

        tokens = serializer.validated_data
        token_obj = AccessToken(tokens['access'])
        user = self.get_user(token_obj)
        user.refreshed_tokens = tokens
        return user, token_obj


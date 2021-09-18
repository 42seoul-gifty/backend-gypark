from django.conf import settings

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.views import LogoutView

from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from .permissions import OwnerPermission
from .serializers import UserSerializer
from .models import User


class CustomSocialLoginView(SocialLoginView):
    def get(self, request, *args, **kwargs):
        self.request = request
        data = {'code': self.request.headers.get('Authorization-Code')}
        self.serializer = self.get_serializer(data=data)

        if not self.serializer.is_valid():
            return Response(self.serializer.errors, status=HTTP_400_BAD_REQUEST)

        self.login()
        return self.get_response()


class KakaoLoginView(CustomSocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    callback_url = settings.KAKAO_CALLBACK_URI
    client_class = OAuth2Client


class NaverLoginView(CustomSocialLoginView):
    adapter_class = NaverOAuth2Adapter
    callback_url = settings.NAVER_CALLBACK_URI
    client_class = OAuth2Client


class TokenRefreshView(get_refresh_view()):
    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['refresh'] = request.data['refresh_token']
        return super().post(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        response.data['access_token'] = response.data.pop('access', '')
        response.data['refresh_token'] = response.data.pop('refresh', '')
        return super().finalize_response(request, response, *args, **kwargs)


class LogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['refresh'] = request.data.get('refresh_token')
        return self.logout(request)


class UserDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated, OwnerPermission)
    serializer_class = UserSerializer
    queryset = User.objects.all()

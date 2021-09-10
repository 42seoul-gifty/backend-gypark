from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from dj_rest_auth.registration.views import SocialLoginView

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
    callback_url = 'http://localhost:8000/login/kakao'
    client_class = OAuth2Client


class NaverLoginView(CustomSocialLoginView):
    adapter_class = NaverOAuth2Adapter
    callback_url = 'http://localhost:8000/login/naver'
    client_class = OAuth2Client


class UserDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated, OwnerPermission)
    serializer_class = UserSerializer
    queryset = User.objects.all()

from django.contrib.auth.models import update_last_login

from rest_framework.generics import (
    GenericAPIView,
    RetrieveAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    KakaoLoginSerializer,
    LogoutSerializer,
    NaverLoginSerializer,
    UserSerializer
)
from .models import User
from .permissions import OwnerPermission


class SocialLoginView(GenericAPIView):
    serializer_class = None

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            serializer = self.serializer_class(instance=user, data=request.data)
        except User.DoesNotExist:
            serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'errors': serializer.errors})

        user = serializer.save()
        update_last_login(None, user)
        return Response(UserSerializer(user).data)


class KakaoLoginView(SocialLoginView):
    serializer_class = KakaoLoginSerializer


class NaverLoginView(SocialLoginView):
    serializer_class = NaverLoginSerializer


class LogoutView(GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'errors': serializer.errors})

        user = User.objects.get(
            token=serializer.validated_data['token']
        )
        user.token = ''
        user.save()

        return Response()


class UserDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated, OwnerPermission)
    serializer_class = UserSerializer
    queryset = User.objects.all()


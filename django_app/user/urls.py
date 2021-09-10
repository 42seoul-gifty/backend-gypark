from django.urls import path

from dj_rest_auth.views import (
    LoginView,
    LogoutView
)
from dj_rest_auth.jwt_auth import get_refresh_view

from .views import (
    KakaoLoginView,
    NaverLoginView,
    UserDetailView
)


app_name = 'user'

urlpatterns = [
    path('login/kakao', KakaoLoginView.as_view(), name='login_kakao'),
    path('login/naver', NaverLoginView.as_view(), name='lgoin_naver'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('token/refresh', get_refresh_view().as_view(), name='token_refresh'),

    path('users/<int:pk>', UserDetailView.as_view(), name='detail'),
]


from django.urls import path

from dj_rest_auth.views import (
    LoginView,
    LogoutView
)

from .views import (
    KakaoLoginView,
    NaverLoginView,
    TokenRefreshView,
    UserDetailView
)


app_name = 'user'

urlpatterns = [
    path('login/kakao', KakaoLoginView.as_view(), name='login_kakao'),
    path('login/naver', NaverLoginView.as_view(), name='lgoin_naver'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/<int:pk>', UserDetailView.as_view(), name='detail'),
]


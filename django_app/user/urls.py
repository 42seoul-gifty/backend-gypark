from django.urls import path
from .views import *


app_name = 'user'

urlpatterns = [
    path('login/kakao', KakaoLoginView.as_view(), name='login_kakao'),
    path('login/naver', NaverLoginView.as_view(), name='lgoin_naver'),
    path('logout', LogoutView.as_view(), name='logout'),

    path('users/<int:pk>', UserDetailView.as_view(), name='detail'),
]

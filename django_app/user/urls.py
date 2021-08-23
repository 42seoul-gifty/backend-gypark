from django.urls import path
from .views import *
from .test_views import *

app_name = 'user'

urlpatterns = [
    path('login/kakao', KakaoLoginView.as_view(), name='login_kakao'),

# test_views
    path('login/kakao/test', KakaoLoginTestView.as_view(), name='login_kakao_test'),
]

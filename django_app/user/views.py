from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from rest_framework.authentication import BasicAuthentication

from gifty.authentication import CsrfExemptSessionAuthentication


class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

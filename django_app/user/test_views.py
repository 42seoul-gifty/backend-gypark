from django.views.generic import TemplateView


class KakaoLoginTestView(TemplateView):
    template_name = 'user/test/login_kakao.html'

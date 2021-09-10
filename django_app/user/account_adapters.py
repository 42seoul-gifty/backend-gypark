from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from rest_framework.serializers import ValidationError

from .models import User


class GiftySocialAccountAapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user

        if user.pk == None and User.objects.filter(email=user.email).exists():
            raise ValidationError(f'이미 가입된 이메일 입니다.')

        social_account = sociallogin.account
        extra_data = social_account.extra_data

        if social_account.provider == 'kakao':
            user.nickname = extra_data['properties']['nickname']
        elif social_account.provider == 'naver':
            user.nickname = extra_data['nickname']

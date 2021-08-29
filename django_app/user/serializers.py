from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
)

from .models import User


class SocialLoginSerializer(ModelSerializer):
    provider = ''

    class Meta:
        model = User
        fields = ('email', 'nickname', 'token')
        extra_kwargs = {'token': {'required': True, 'allow_blank': False}}

    def validate_email(self, email):
        users = User.objects.filter(email=email)

        if users.exists() and users[0].login_type != self.provider:
            raise ValidationError(
                f'This email is already registered with {users[0].login_type}'
            )

        return email

    def validate(self, attrs):
        email = attrs['email']
        token = attrs['token']

        token_user = User.objects.filter(token=token)

        # 이 로직은 validate_token의 임시 로직입니다.
        if token_user.exists() and token_user[0].email != email:
            raise ValidationError(
                'The same token is being used by another user.'
            )

        return attrs

    def update(self, instance, validated_data):
        instance.token = validated_data['token']
        instance.save()
        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.login_type = self.provider
        instance.set_unusable_password()
        instance.save()
        return instance


class KakaoLoginSerializer(SocialLoginSerializer):
    provider = 'kakao'

    def validate_token(self, token):
        '''
        이메일에 대한 토큰이 유효한지 확인할 필요가 있음.
        '''
        return token


class NaverLoginSerializer(SocialLoginSerializer):
    provider = 'naver'

    def validate_token(self, token):
        '''
        이메일에 대한 토큰이 유효한지 확인할 필요가 있음.
        '''
        return token


class LogoutSerializer(Serializer):
    token = CharField(max_length=128)

    def validate_token(self, token):
        if not User.objects.filter(token=token).exists():
            raise ValidationError('Unregistered token.')

        return token


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'nickname')


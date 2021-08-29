from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
)

from .models import User


class KakaoLoginSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'nickname', 'token')
        extra_kwargs = {'token': {'required': True, 'allow_blank': False}}

    def validate_token(self, token):
        '''
        이메일에 대한 토큰이 유효한지 확인할 필요가 있음.
        '''
        return token

    def validate_email(self, email):
        users = User.objects.filter(email=email)

        if users.exists() and users[0].login_type != 'kakao':
            raise ValidationError(
                f'This email is already registered with {users[0].login_type}'
            )

        return email

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.set_unusable_password()
        instance.save()
        return instance


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


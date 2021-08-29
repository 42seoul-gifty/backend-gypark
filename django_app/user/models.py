from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = None
    email = models.EmailField(
        '이메일',
        unique=True
    )
    nickname = models.CharField(
        '닉네임',
        max_length=32
    )
    token = models.CharField(
        '토큰',
        blank=True,
        max_length=128
    )
    login_type = models.CharField(
        '로그인 타입',
        blank=True,
        max_length=32,
        choices=[
            ('kakao', 'kakao'),
            ('naver', 'naver'),
            ('gifty', 'gifty'),
        ]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

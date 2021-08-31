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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

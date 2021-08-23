from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = None
    email = models.EmailField(
        '이메일',
        blank=True,
        unique=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    nickname = models.CharField(
        '닉네임',
        blank=True,
        max_length=32,
    )

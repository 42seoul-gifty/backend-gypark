from django.db import models
from .base import BaseModel
from .manager import AppManager


class GenderCategory(BaseModel):
    value = models.CharField(max_length=16)
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    manager = models.ForeignKey(AppManager, on_delete=models.CASCADE, default=1, related_name='genders')


class AgeCategory(BaseModel):
    min = models.PositiveIntegerField(null=True, blank=True)
    max = models.PositiveIntegerField(null=True, blank=True)
    str = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    manager = models.ForeignKey(AppManager, on_delete=models.CASCADE, default=1, related_name='ages')


class PriceCategory(BaseModel):
    value = models.PositiveIntegerField()
    str = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    manager = models.ForeignKey(AppManager, on_delete=models.CASCADE, default=1, related_name='prices')


class ProductCategory(BaseModel):
    value = models.CharField(max_length=32)

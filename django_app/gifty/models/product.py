from django.db import models
from .base import BaseModel
from .category import (
    PriceCategory,
    ProductCategory,
    GenderCategory,
    AgeCategory
)


class Product(BaseModel):
    id = models.BigAutoField(primary_key=True, verbose_name='코드')
    name = models.CharField(max_length=128, verbose_name='상품명')
    category = models.ForeignKey(ProductCategory, verbose_name='상품유형', related_name='products', on_delete=models.CASCADE)
    thumbnail = models.ImageField(verbose_name='썸네일')
    description = models.TextField(blank=True, verbose_name='상품소개')
    vendor = models.CharField(max_length=64, verbose_name='판매처')
    views = models.PositiveIntegerField(default=0, verbose_name='노출수')
    likes = models.ManyToManyField('Receiver', related_name='likes', verbose_name='좋아요')
    dislikes = models.ManyToManyField('Receiver', related_name='dislikes', verbose_name='싫어요')
    gender = models.ManyToManyField(GenderCategory, verbose_name='성별', related_name='products')
    age = models.ManyToManyField(AgeCategory, verbose_name='연령', related_name='products')
    price = models.ForeignKey(PriceCategory, verbose_name='가격', related_name='products', on_delete=models.CASCADE)


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='상품 상세 이미지')

from django.db import models
from .base import BaseModel
from .user import User
from .product import Product
from .category import *


class Receiver(BaseModel):
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    address = models.CharField(max_length=128)
    address_detail = models.CharField(max_length=128)


class Order(BaseModel):
    giver = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Receiver, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='order')
    gender = models.ManyToManyField(GenderCategory, related_name="orders")
    age = models.ManyToManyField(AgeCategory, related_name='orders')
    price = models.ForeignKey(PriceCategory, related_name='orders', on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    state = models.CharField(max_length=32, choices=[
        ('결제완료', '결제완료'),
        ('선택완료', '선택완료'),
        ('배송중', '배송중'),
        ('배송완료', '배송완료')
    ])

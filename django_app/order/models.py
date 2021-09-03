from django.core import validators
from django.db import models

from gifty.models import (
    BaseModel,
    Product,
    GenderCategory,
    AgeCategory,
    PriceCategory
)
from gifty.validators import phone_validator
from user.models import User


class Order(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    giver_name = models.CharField(
        max_length=128
    )
    giver_phone = models.CharField(
        max_length=128,
        validators=(phone_validator, )
    )
    gender = models.ManyToManyField(
        GenderCategory,
        verbose_name='성별',
        related_name='orders'
    )
    age = models.ManyToManyField(
        AgeCategory,
        verbose_name='연령',
        related_name='orders'
    )
    price = models.ForeignKey(
        PriceCategory,
        verbose_name='가격',
        related_name='orders',
         on_delete=models.DO_NOTHING
    )


class Receiver(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='receivers'
    )
    name = models.CharField(
        max_length=128
    )
    phone = models.CharField(
        max_length=32,
        validators=(phone_validator, )
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.DO_NOTHING,
        related_name='receivers',
        null=True
    )
    shipment_status = models.CharField(
        max_length=32,
        choices=[
            ('미선택', '미선택'),
            ('배송준비', '배송준비'),
            ('배송중', '배송중'),
            ('배송완료', '배송완료'),
        ],
        default='미선택'
    )


class Address(BaseModel):
    address = models.CharField(
        max_length=128,
    )
    detail = models.CharField(
        max_length=128,
        blank=True
    )
    post_code = models.CharField(
        max_length=32
    )
    receiver = models.OneToOneField(
        Receiver,
        on_delete=models.CASCADE,
        related_name='address'
    )


class Payment(BaseModel):
    merchant_uid = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    imp_uid = models.CharField(
        max_length=128,
    )
    amount = models.PositiveIntegerField(
        default=0
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    status = models.CharField(
        max_length=64,
        choices=[
            ('결제대기', '결제대기'),
            ('결제실패', '결제실패'),
            ('결제완료', '결제완료'),
        ],
        default='결제대기'
    )

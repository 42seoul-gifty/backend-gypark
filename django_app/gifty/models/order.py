from django.db import models
from .base import BaseModel
from .user import User
from .product import Product
from .category import *

from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Receiver(BaseModel):
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='receivers')
    address = models.CharField(max_length=128)
    address_detail = models.CharField(max_length=128)
    shipment_status = models.CharField(max_length=32, choices=[
        ('배송준비', '배송준비'),
        ('배송중', '배송중'),
        ('배송완료', '배송완료'),
    ])


class Payment(BaseModel):
    imp_uid = models.CharField(max_length=128, blank=True)
    amount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=64, choices=[
        ('결제대기', '결제대기'),
        ('결제실패', '결제실패'),
        ('결제완료', '결제완료'),
    ])

    @property
    def merchant_uid(self):
        return str(self.order.pk)


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    giver_name = models.CharField(max_length=128)
    giver_phone = models.CharField(max_length=128)
    receiver = models.OneToOneField(Receiver, on_delete=models.DO_NOTHING, related_name='order')
    payment = models.OneToOneField(Payment, on_delete=models.DO_NOTHING, related_name='order')
    gender = models.ManyToManyField(GenderCategory, verbose_name='성별', related_name='orders')
    age = models.ManyToManyField(AgeCategory, verbose_name='연령', related_name='orders')
    price = models.ForeignKey(PriceCategory, verbose_name='가격', related_name='orders', on_delete=models.DO_NOTHING)


@receiver(pre_delete, sender=Order)
def on_order_delete(sender, instance, **kwargs):
    if instance.payment:
        instance.payment.delete()
    if instance.receiver:
        instance.receiver.delete()

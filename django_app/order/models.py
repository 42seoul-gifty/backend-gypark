import string
import random

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
    uuid = models.CharField(
        max_length=6
    )

    @property
    def user(self):
        return self.order.user

    @property
    def link(self):
        return f'front-host/receiver/{self.uuid}'

    def set_uuid(self):
        # https://stackoverflow.com/questions/13484726/safe-enough-8-character-short-unique-random-string
        if self.uuid:
            return

        alphabet = string.ascii_lowercase + string.digits
        uuid = ''.join(random.choices(alphabet, k=6))
        receiver = Receiver.objects.filter(uuid=uuid).exclude(
            shipment_status='배송완료'
        )

        if receiver.exists():
            self.set_uuid()

        self.uuid = uuid

    @property
    def products_list(self):
        order = self.order
        filter_kwargs = {
            'price': order.price,
            'gender__in': order.gender.all(),
            'age__in': order.age.all()
        }
        return Product.objects.filter(**filter_kwargs)



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

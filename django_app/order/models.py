import string
import random
import json

from django.db import models
from django.shortcuts import get_object_or_404
from django.conf import settings

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
        on_delete=models.CASCADE,
        related_name='orders',
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

    class Meta:
        verbose_name = '배송'
        verbose_name_plural = '배송관리'

    @property
    def receiver(self):
        return self.receivers.first()


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
    sms_response = models.TextField(
        'sms 발송 결과',
        blank=True
    )

    @property
    def user(self):
        return self.order.user

    @property
    def link(self):
        return f'{settings.FRONT_HOST}/receiver/{self.uuid}'

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
        return Product.objects.actived_for_receiver().filter(**filter_kwargs)

    @property
    def sms_message(self):
        return f'{self.order.giver_name}님이 보내신 선물이 도착했습니다. {self.link}'

    @property
    def sms_request_id(self):
        return json.loads(self.sms_response)['requestId']

    @staticmethod
    def get_available_or_404(uuid):
        queryset = Receiver.objects.exclude(shipment_status='배송완료')
        return get_object_or_404(queryset, uuid=uuid)



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

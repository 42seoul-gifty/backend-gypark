import requests

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    SerializerMethodField,
    DateTimeField,
    PrimaryKeyRelatedField
)
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied
)

from .models import (
    Order,
    Receiver,
    Address,
    Payment
)


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'post_code',
            'address',
            'detail'
        )


class ReceiverCreateSerializer(ModelSerializer):
    class Meta:
        model = Receiver
        fields = (
            'name',
            'phone'
        )


class ReceiverSerializer(ModelSerializer):
    address = SerializerMethodField()

    class Meta:
        model = Receiver
        fields = (
            'id',
            'name',
            'phone',
            'product',
            'address',
        )

    def get_address(self, obj):
        try:
            return AddressSerializer(obj.address).data
        except ObjectDoesNotExist:
            return AddressSerializer(None).data


class OrderCreateSerializer(ModelSerializer):
    receiver_name = CharField()
    receiver_phone = CharField()

    class Meta:
        model = Order
        fields = (
            'giver_name',
            'giver_phone',
            'receiver_name',
            'receiver_phone',
            'gender',
            'age',
            'price',
        )

    def validate(self, attrs):
        if hasattr(self, 'receiver_serializer'):
            return attrs

        self.receiver_serializer = ReceiverCreateSerializer(
            data={
                'name': attrs.pop('receiver_name'),
                'phone': attrs.pop('receiver_phone'),
            }
        )
        self.receiver_serializer.is_valid(raise_exception=True)

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        order = super().create(validated_data)
        self.receiver_serializer.save(order=order)
        return order


class OrderSerializer(ModelSerializer):
    receiver = SerializerMethodField()
    preference = SerializerMethodField()
    status = SerializerMethodField()
    order_date = DateTimeField(source='created')

    class Meta:
        model = Order
        fields = (
            'giver_name',
            'giver_phone',
            'receiver',
            'order_date',
            'preference',
            'status'
        )

    # 현 기능에서 수신자는 한명만
    def get_receiver(self, obj):
        return ReceiverSerializer(obj.receivers.first()).data

    def get_preference(self, obj):
        return {
            'age': obj.age.values_list('id', flat=True),
            'gender': obj.gender.values_list('id', flat=True),
            'price': obj.price.id
        }

    def get_status(self, obj):
        try:
            return obj.payment.status
        except ObjectDoesNotExist:
            return Payment._meta.get_field('status').get_default()


class PaymentValidationSerializer(ModelSerializer):
    merchant_uid = PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Payment
        fields = (
            'merchant_uid',
            'imp_uid',
        )

    def validate(self, attrs):
        order = attrs['merchant_uid']
        imp_uid = attrs['imp_uid']
        access_token = self.get_access_token()
        payment_data = self.get_payment_data(access_token, imp_uid)

        if order.id == payment_data['merchant_uid'] and \
            imp_uid == payment_data['imp_uid'] and \
            order.price.value == int(payment_data['amount']):
            return attrs

        raise ValidationError('주문 정보가 일치하지 않습니다.')

    def create(self, validated_data):
        payment = Payment.objects.update_or_create(
            **validated_data,
            amount=validated_data['merchant_uid'].price.value,
            status='결제완료'
        )
        return payment

    def get_access_token(self):
        url = 'https://api.iamport.kr/users/getToken'
        data = {
            'imp_key': settings.IMP_KEY,
            'imp_secret': settings.IMP_SECRET
        }
        res = requests.post(url, data=data)

        try:
            return res.json()['response']['access_token']
        except:
            raise ValidationError('Iamport server error')

    def get_payment_data(self, access_token, imp_uid):
        url = f'https://api.iamport.kr/payments/{imp_uid}'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            raise ValidationError(res.json()['message'])

        return res.json()['response']

import os
from copy import deepcopy

from django.conf import settings
from django.test import (
    TestCase,
    tag
)

from schema import (
    And,
    Schema,
    Or
)

from gifty.tests.test_models import (
    get_dummy_age,
    get_dummy_gender,
    get_dummy_price,
    get_dummy_product,
    get_dummy_product_category,
    get_dummy_appmanager,
)
from gifty.tests.test_views import ProductDetailViewTest
from user.tests.test_models import (
    get_jwt,
    jwt_to_headers,
)
from .test_models import (
    get_dummy_address,
    get_dummy_order,
    get_dummy_receiver
)
from gifty.models import (
    PriceCategory,
    Product
)
from ..models import Order, Receiver
from ..sms import search_sms_request


class PaymentValidationViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.merchant_uid = os.environ.get('TEST_MERCHANT_UID')
        cls.imp_uid = os.environ.get('TEST_IMP_UID')
        cls.amount = int(os.environ.get('TEST_AMOUNT'))

        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))

        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_price(value=cls.amount)
        get_dummy_product()
        get_dummy_order()

    def test_비인증(self):
        data = {
            'merchant_uid': self.merchant_uid,
            'imp_uid': self.imp_uid
        }
        response = self.client.post('/payment/validation', data=data)
        self.assertEqual(response.status_code, 401)

    def test_다른유저(self):
        headers = jwt_to_headers(get_jwt(
            'test2@test.co.kr',
            '1234'
        ))
        data = {
            'merchant_uid': self.merchant_uid,
            'imp_uid': self.imp_uid
        }
        response = self.client.post('/payment/validation', data=data, **headers)
        self.assertEqual(response.status_code, 403)


    def test_정상체크(self):
        data = {
            'merchant_uid': self.merchant_uid,
            'imp_uid': self.imp_uid
        }
        response = self.client.post('/payment/validation', data=data, **self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))

    def test_없는_merchant_uid(self):
        data = {
            'merchant_uid': 42,
            'imp_uid': self.imp_uid
        }
        response = self.client.post('/payment/validation', data=data, **self.headers)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))

    def test_없는_imp_uid(self):
        data = {
            'merchant_uid': self.merchant_uid,
            'imp_uid': 42,
        }
        response = self.client.post('/payment/validation', data=data, **self.headers)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))

    def test_일치하지않음(self):
        PriceCategory.objects.filter(orders__id=self.merchant_uid) \
                             .update(value=self.amount + 1)
        data = {
            'merchant_uid': self.merchant_uid,
            'imp_uid': self.imp_uid
        }
        response = self.client.post('/payment/validation', data=data, **self.headers)
        PriceCategory.objects.filter(orders__id=self.merchant_uid) \
                             .update(value=self.amount)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))


class OrderListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_price()
        get_dummy_product()

        cls.order_count = 3
        for _ in range(cls.order_count):
            get_dummy_order()

    def test_비인증(self):
        res = self.client.get('/users/1/orders')
        self.assertEqual(res.status_code, 401)

    def test_다른유저(self):
        get_jwt(
            'test2@test.co.kr',
            '1234'
        )
        res = self.client.get('/users/2/orders', **self.headers)
        self.assertEqual(res.status_code, 403)

    def test_없는유저(self):
        res = self.client.get('/users/42/orders', **self.headers)
        self.assertEqual(res.status_code, 404)

    def test_정상조회(self):
        res = self.client.get('/users/1/orders', **self.headers)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertTrue(data['success'])

        orders = data['data']
        self.assertTrue(isinstance(orders, list))
        self.assertEqual(len(orders), self.order_count)


class OrderCreateViewTest(TestCase):
    success_schema = Schema(
        {
            'success': bool,
            'data': {
                'id': int,
                'merchant_uid': str,
                'receiver_id': And([str], len)
            }
        }
    )

    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_age()
        get_dummy_price()
        get_dummy_product()

    def test_비인증(self):
        res = self.client.post('/users/1/orders')
        self.assertEqual(res.status_code, 401)

    def test_다른유저(self):
        get_jwt(
            'test2@test.co.kr',
            '1234'
        )
        res = self.client.post('/users/2/orders', **self.headers)
        self.assertEqual(res.status_code, 403)

    def test_없는유저(self):
        res = self.client.post('/users/42/orders', **self.headers)
        self.assertEqual(res.status_code, 404)

    def test_정상생성(self):
        data = {
            "giver_name": "test_giver",
            "giver_phone": "01012345678",
            "receiver_name": "test_receiver",
            "receiver_phone": "01012345678",
            "gender": [1],
            "age": [1, 2],
            "price": 1,
        }
        res = self.client.post('/users/1/orders', data=data, **self.headers)
        self.assertEqual(res.status_code, 201)

        self.assertTrue(self.success_schema.is_valid(res.json()))

        order = Order.objects.first()
        self.assertTrue(order.giver_name == data['giver_name'])
        self.assertTrue(order.giver_phone == data['giver_phone'])
        self.assertTrue(order.receiver.name == data['receiver_name'])
        self.assertTrue(order.receiver.phone == data['receiver_phone'])
        self.assertTrue(list(order.gender.all().values_list('id', flat=True)) == data['gender'])
        self.assertTrue(list(order.age.all().values_list('id', flat=True)) == data['age'])
        self.assertTrue(order.price.id == data['price'])


class ReceiverDetailViewTest(TestCase):
    success_dict = {
        "success": True,
        "data": {
            "id": str,
            "name": str,
            "phone": str,
            "product": Or(None, ProductDetailViewTest.success_schema.schema['data']),
            "address": {
                "post_code": str,
                "address": str,
                "address_detail": str,
            }
        },
    }
    success_schema = Schema(success_dict)

    selected_product_dict = deepcopy(success_dict)
    selected_product_dict['data']['product'] = ProductDetailViewTest.success_schema.schema['data']
    selected_product_schema = Schema(selected_product_dict)

    not_selected_product_dict = deepcopy(success_dict)
    not_selected_product_dict['data']['product'] = None
    not_selected_product_schema = Schema(not_selected_product_dict)

    @classmethod
    def setUpTestData(cls):
        get_jwt(
            'test@test.co.kr',
            '1234'
        )
        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_age()
        get_dummy_price()
        product = get_dummy_product()
        get_dummy_order()

        cls.not_selected_product_receiver = get_dummy_receiver()
        cls.selected_product_receiver = get_dummy_receiver(
            product=product,
        )
        get_dummy_address(receiver_id=cls.selected_product_receiver.id)

    def test_없는_수신자(self):
        res = self.client.get(f'/receiver/42')
        self.assertEqual(res.status_code, 404)

    def test_상품을_선택한_수신자(self):
        uuid = self.selected_product_receiver.uuid
        res = self.client.get(f'/receiver/{uuid}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(self.selected_product_schema.is_valid(res.json()))

    def test_상품을_선택하지않은_수신자(self):
        uuid = self.not_selected_product_receiver.uuid
        res = self.client.get(f'/receiver/{uuid}')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(self.not_selected_product_schema.is_valid(res.json()))


class ReceiverPatchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_jwt(
            'test@test.co.kr',
            '1234'
        )
        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_age()
        get_dummy_price()
        get_dummy_product()
        get_dummy_order()
        cls.receiver = get_dummy_receiver()

    def test_없는_수신자(self):
        res = self.client.patch('/receiver/42')
        self.assertEqual(res.status_code, 404)

    def test_정상수정(self):
        data = {
            'product_id': 1,
            'post_code': '우편 번호',
            'address': '주소',
            'address_detail': '상세 주소',
            'likes': [1],
            'dislikes': [],
        }
        uuid = self.receiver.uuid
        res = self.client.patch(f'/receiver/{uuid}', data=data, content_type='application/json')

        receiver = Receiver.objects.get(id=self.receiver.id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(receiver.product_id, data['product_id']),
        self.assertEqual(list(receiver.likes.all().values_list('id', flat=True)), data['likes'])
        self.assertEqual(list(receiver.dislikes.all().values_list('id', flat=True)), data['dislikes'])
        self.assertEqual(receiver.address.address, data['address'])
        self.assertEqual(receiver.address.address_detail, data['address_detail'])
        self.assertEqual(receiver.address.post_code, data['post_code'])


class OrderDetailViewTest(TestCase):
    success_schema = Schema(
        {
            'success': True,
            'data': {
                'id': int,
                'giver_name': str,
                'giver_phone': str,
                'receiver': ReceiverDetailViewTest.success_schema.schema['data'],
                'order_date': str,
                'preference': {
                    'age': [int],
                    'gender': [int],
                    'price': int,
                },
                'status': str,
            }
        }
    )

    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_price()
        get_dummy_product()
        get_dummy_order()
        get_dummy_receiver()

    def test_비인증(self):
        res = self.client.get('/users/1/orders/1')
        self.assertEqual(res.status_code, 401)

    def test_다른유저(self):
        get_jwt(
            'test2@test.co.kr',
            '1234'
        )
        res = self.client.get('/users/2/orders/1', **self.headers)
        self.assertEqual(res.status_code, 403)

    def test_없는유저(self):
        res = self.client.get('/users/42/orders/1', **self.headers)
        self.assertEqual(res.status_code, 404)

    def test_없는주문정보(self):
        res = self.client.get('/users/1/orders/42', **self.headers)
        self.assertEqual(res.status_code, 404)

    def test_정상조회(self):
        res = self.client.get('/users/1/orders/1', **self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(self.success_schema.is_valid(res.json()))


class OrderDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_price()
        get_dummy_product()
        get_dummy_order()
        get_dummy_receiver()

    def test_비인증(self):
        res = self.client.delete('/users/1/orders/1')
        self.assertEqual(res.status_code, 401)

    def test_다른유저(self):
        get_jwt(
            'test2@test.co.kr',
            '1234'
        )
        res = self.client.delete('/users/2/orders/1', **self.headers)
        self.assertEqual(res.status_code, 403)

    def test_없는유저(self):
        res = self.client.delete('/users/42/orders/1', **self.headers)
        self.assertEqual(res.status_code, 404)

    def test_없는주문정보(self):
        res = self.client.delete('/users/1/orders/42', **self.headers)
        self.assertEqual(res.status_code, 404)

    def test_정상삭제(self):
        res = self.client.delete('/users/1/orders/1', **self.headers)
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Order.objects.exists())
        self.assertFalse(Receiver.objects.exists())


class ReceiverDataSetViewTest(TestCase):
    success_schema = Schema(
        {
            'success': True,
            'data': {
                'giver_name': str,
                'giver_phone': str,
                'products': [ProductDetailViewTest.success_schema.schema['data']]
            }
        }
    )
    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_price()
        get_dummy_product()
        get_dummy_order()
        cls.receiver = get_dummy_receiver()

    def test_없는_수신자(self):
        res = self.client.get('/receiver/42/choice')
        self.assertEqual(res.status_code, 404)

    def test_정상조회(self):
        uuid = self.receiver.uuid
        res = self.client.get(f'/receiver/{uuid}/choice')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(self.success_schema.is_valid(res.json()))

    def test_카테고리_비활성화시_상품리스트_필터링(self):
        uuid = self.receiver.uuid
        PriceCategory.objects.update(is_active=False)
        res = self.client.get(f'/receiver/{uuid}/choice')
        PriceCategory.objects.update(is_active=True)

        self.assertEqual(res.status_code, 200)

        products = res.json()['data']['products']
        self.assertEqual(len(products), 1)

    def test_상품자체_비활성화_필터링(self):
        uuid = self.receiver.uuid
        Product.objects.update(is_active=False)
        res = self.client.get(f'/receiver/{uuid}/choice')
        Product.objects.update(is_active=True)

        self.assertEqual(res.status_code, 200)

        products = res.json()['data']['products']
        self.assertEqual(len(products), 0)


class ReceiverSendSMSViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()
        get_dummy_product_category()
        get_dummy_gender()
        get_dummy_age()
        get_dummy_age()
        get_dummy_price()
        get_dummy_product()
        get_dummy_order(giver_name='송신자')
        cls.receiver = get_dummy_receiver(
            phone=os.environ['TEST_RECEIVER_PHONE'],
            name='수신자'
        )

    @tag('need_pay')
    def test_정상발송(self):
        uuid = self.receiver.uuid
        res = self.client.post(f'/receiver/{uuid}/send', **self.headers)
        self.assertEqual(res.status_code, 202)

        self.receiver = Receiver.objects.first()
        res = search_sms_request(self.receiver.sms_request_id)
        self.assertEqual(res.status_code, 200)

        message = res.json()['messages'][0]
        self.assertEqual(message['from'], settings.SMS_PHONE_NUMBER)
        self.assertEqual(message['to'], self.receiver.phone)

import os
from copy import deepcopy

from django.test import TestCase

from schema import (
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
from gifty.models import PriceCategory
from ..models import Order


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

        res_data = res.json()
        self.assertTrue(res_data['success'])

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
                "detail": str,
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


class OrderDetailViewTest(TestCase):
    success_schema = Schema(
        {
            'success': True,
            'data': {
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

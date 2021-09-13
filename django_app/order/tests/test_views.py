import os

from django.test import TestCase

from gifty.tests.test_models import (
    get_dummy_age,
    get_dummy_gender,
    get_dummy_price,
    get_dummy_product,
    get_dummy_product_category,
    get_dummy_appmanager,
)
from user.tests.test_models import (
    get_jwt,
    jwt_to_headers,
)
from .test_models import get_dummy_order
from gifty.models import PriceCategory


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





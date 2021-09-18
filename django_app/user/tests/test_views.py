from django.test import TestCase

from schema import Schema

from .test_models import (
    jwt_to_headers,
    get_jwt,
)

class UserDetailViewTest(TestCase):
    success_schema = Schema(
        {
            'success': True,
            'data': {
                'id': int,
                'nickname': str,
                'email': str
            }
        }
    )

    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))

    def test_비인증(self):
        res = self.client.get('/users/1')
        self.assertEqual(res.status_code, 401)

    def test_없는유저(self):
        res = self.client.get('/users/42', **self.headers)
        self.assertEqual(res.status_code, 404)

    def test_다른유저(self):
        headers = jwt_to_headers(get_jwt(
            'test2@test.co.kr',
            '1234'
        ))
        res = self.client.get('/users/1', **headers)
        self.assertEqual(res.status_code, 403)

    def test_정상조회(self):
        res = self.client.get('/users/1', **self.headers)
        self.assertTrue(self.success_schema.is_valid(res.json()))


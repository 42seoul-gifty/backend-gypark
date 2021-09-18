import os
from urllib.parse import (
    urlparse,
    parse_qs,
)

from django.conf import settings
from django.test import (
    TestCase,
    Client,
    tag
)

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from schema import Schema

from .test_models import (
    jwt_to_headers,
    get_jwt,
    get_dummy_socialapp,
)
from ..models import User


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


class KakaoLoginViewTest(TestCase):
    success_schema = Schema(
        {
            'success': True,
            'data': {
                'access_token': str,
                'refresh_token': str,
                'user': UserDetailViewTest.success_schema.schema['data']
            }
        }
    )

    @classmethod
    def setUpTestData(cls):
        cls.redirect_uri = settings.KAKAO_CALLBACK_URI
        cls.client_id = os.environ['TEST_KAKAO_CLIENT_ID']
        cls.browser = webdriver.Chrome(os.environ['TEST_CHROMEDRIVER_PATH'])
        cls.email = os.environ['TEST_KAKAO_EMAIL']
        cls.password = os.environ['TEST_KAKAO_PASSWORD']

        get_dummy_socialapp(
            provider='kakao',
            name='카카오',
            client_id=cls.client_id
        )


    @classmethod
    def tearDownClass(cls):
        cls.browser.close()

    @tag('selenium')
    def test_없는_인가코드(self):
        client = Client(raise_request_exception=False)
        code = '42'
        res = client.get('/login/kakao', **{'HTTP_Authorization-Code': code})
        self.assertEqual(res.status_code, 500)

    @tag('selenium')
    def test_정상로그인(self):
        code = self._get_kakao_auth_code()
        res = self.client.get('/login/kakao', **{'HTTP_Authorization-Code': code})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(self.success_schema.is_valid(res.json()))

        user = User.objects.first()
        self.assertEqual(user.socialaccount_set.first().provider, 'kakao')
        self.assertTrue(user.nickname)

    def _get_kakao_auth_code(self):
        url = ('https://kauth.kakao.com/oauth/authorize?'
              f'client_id={self.client_id}&'
              f'redirect_uri={self.redirect_uri}&'
              f'response_type=code')
        self.browser.get(url)
        self.browser.find_element_by_name('email').send_keys(self.email)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_class_name('submit').click()
        wait = WebDriverWait(self.browser, 5)
        wait.until(EC.url_changes(self.browser.current_url))

        parsed = urlparse(self.browser.current_url)
        code = parse_qs(parsed.query)['code'][0]

        return code

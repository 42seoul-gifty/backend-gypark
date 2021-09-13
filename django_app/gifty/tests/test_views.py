from itertools import (
    chain,
    combinations,
    product
)

from django.test import (
    TestCase,
    Client
)

from .test_models import (
    get_dummy_age,
    get_dummy_gender,
    get_dummy_price,
    get_dummy_product,
    get_dummy_product_category,
    get_dummy_appmanager,
)
from ..models import (
    GenderCategory,
    AgeCategory,
    PriceCategory,
)
from user.models import User
from user.tests.test_models import (
    get_jwt,
    jwt_to_headers
)


def all_subsets(ss, start=0):
    return chain(*map(lambda x: combinations(ss, x), range(start, len(ss)+1)))


class ProductListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_dummy_appmanager()
        get_dummy_product_category()
        genders = [get_dummy_gender().id, get_dummy_gender().id]
        ages = [get_dummy_age().id, get_dummy_age().id]
        prices = [get_dummy_price().id, get_dummy_price().id]

        genders_subsets = all_subsets(genders, 1)
        ages_subsets = all_subsets(ages, 1)
        all_combs = product(genders_subsets, ages_subsets, prices)

        '''
        상품  1: 성별=(1,)     나이=(1,)     가격=1
        상품  2: 성별=(1,)     나이=(1,)     가격=2
        상품  3: 성별=(1,)     나이=(2,)     가격=1
        상품  4: 성별=(1,)     나이=(2,)     가격=2
        상품  5: 성별=(1,)     나이=(1, 2)   가격=1
        상품  6: 성별=(1,)     나이=(1, 2)   가격=2
        상품  7: 성별=(2,)     나이=(1,)     가격=1
        상품  8: 성별=(2,)     나이=(1,)     가격=2
        상품  9: 성별=(2,)     나이=(2,)     가격=1
        상품 10: 성별=(2,)     나이=(2,)     가격=2
        상품 11: 성별=(2,)     나이=(1, 2)   가격=1
        상품 12: 성별=(2,)     나이=(1, 2)   가격=2
        상품 13: 성별=(1, 2)   나이=(1,)     가격=1
        상품 14: 성별=(1, 2)   나이=(1,)     가격=2
        상품 15: 성별=(1, 2)   나이=(2,)     가격=1
        상품 16: 성별=(1, 2)   나이=(2,)     가격=2
        상품 17: 성별=(1, 2)   나이=(1, 2)   가격=1
        상품 18: 성별=(1, 2)   나이=(1, 2)   가격=2
        '''
        for i, combs in enumerate(all_combs):
            # print(f'상품{i+1:8}: 성별={str(combs[0]):8} 나이={str(combs[1]):8} 가격={str(combs[2]):8}')
            get_dummy_product(
                gender_ids=combs[0],
                age_ids=combs[1],
                price_id=combs[2]
            )

        data = {
            'email': 'test@test.co.kr',
            'password': '1234',
        }
        user = User.objects.create(email=data['email'])
        user.set_password(data['password'])
        user.save()
        client = Client()
        response = client.post('/login', data=data)
        access_token = response.json()['data']['access_token']
        cls.auth = {
            'HTTP_AUTHORIZATION': f'Bearer {access_token}'
        }

    def test_비인증(self):
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 401)

    def test_필터없이(self):
        response = self.client.get('/products', **self.auth)
        self.assertEqual(response.status_code, 200)

        data = response.json()['data']
        self.assertEqual(len(data), 18)

    def test_필터링_가격(self):
        '''
        상품  1: 성별=(1,)     나이=(1,)     가격=1 O
        상품  2: 성별=(1,)     나이=(1,)     가격=2 X
        상품  3: 성별=(1,)     나이=(2,)     가격=1 O
        상품  4: 성별=(1,)     나이=(2,)     가격=2 X
        상품  5: 성별=(1,)     나이=(1, 2)   가격=1 O
        상품  6: 성별=(1,)     나이=(1, 2)   가격=2 X
        상품  7: 성별=(2,)     나이=(1,)     가격=1 O
        상품  8: 성별=(2,)     나이=(1,)     가격=2 X
        상품  9: 성별=(2,)     나이=(2,)     가격=1 O
        상품 10: 성별=(2,)     나이=(2,)     가격=2 X
        상품 11: 성별=(2,)     나이=(1, 2)   가격=1 O
        상품 12: 성별=(2,)     나이=(1, 2)   가격=2 X
        상품 13: 성별=(1, 2)   나이=(1,)     가격=1 O
        상품 14: 성별=(1, 2)   나이=(1,)     가격=2 X
        상품 15: 성별=(1, 2)   나이=(2,)     가격=1 O
        상품 16: 성별=(1, 2)   나이=(2,)     가격=2 X
        상품 17: 성별=(1, 2)   나이=(1, 2)   가격=1 O
        상품 18: 성별=(1, 2)   나이=(1, 2)   가격=2 X
        '''
        response = self.client.get(
            '/products',
            {
                'gender': [1, 2],
                'age': [1, 2],
                'price': 1
            },
            **self.auth
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()['data']
        self.assertEqual(len(data), 9)

        ids_list = list(map(lambda row: row['id'], data))
        ans_list = [1, 3, 5, 7, 9, 11, 13, 15, 17]
        self.assertEqual(ids_list, ans_list)

    def test_필터링_가격_나이_성별(self):
        '''
        상품  1: 성별=(1,)     나이=(1,)     가격=1 O
        상품  2: 성별=(1,)     나이=(1,)     가격=2 X
        상품  3: 성별=(1,)     나이=(2,)     가격=1 X
        상품  4: 성별=(1,)     나이=(2,)     가격=2 X
        상품  5: 성별=(1,)     나이=(1, 2)   가격=1 O
        상품  6: 성별=(1,)     나이=(1, 2)   가격=2 X
        상품  7: 성별=(2,)     나이=(1,)     가격=1 X
        상품  8: 성별=(2,)     나이=(1,)     가격=2 X
        상품  9: 성별=(2,)     나이=(2,)     가격=1 X
        상품 10: 성별=(2,)     나이=(2,)     가격=2 X
        상품 11: 성별=(2,)     나이=(1, 2)   가격=1 X
        상품 12: 성별=(2,)     나이=(1, 2)   가격=2 X
        상품 13: 성별=(1, 2)   나이=(1,)     가격=1 O
        상품 14: 성별=(1, 2)   나이=(1,)     가격=2 X
        상품 15: 성별=(1, 2)   나이=(2,)     가격=1 X
        상품 16: 성별=(1, 2)   나이=(2,)     가격=2 X
        상품 17: 성별=(1, 2)   나이=(1, 2)   가격=1 O
        상품 18: 성별=(1, 2)   나이=(1, 2)   가격=2 X
        '''
        response = self.client.get(
            '/products',
            {
                'gender': [1],
                'age': [1],
                'price': 1
            },
            **self.auth
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()['data']
        self.assertEqual(len(data), 4)

        ids_list = list(map(lambda row: row['id'], data))
        ans_list = [1, 5, 13, 17]
        self.assertEqual(ids_list, ans_list)

    def test_필터링_일부_비활성(self):
        '''
        상품  1: 성별=(1,)     나이=(1,)     가격=1 X
        상품  2: 성별=(1,)     나이=(1,)     가격=2 X
        상품  3: 성별=(1,)     나이=(2,)     가격=1 X
        상품  4: 성별=(1,)     나이=(2,)     가격=2 X
        상품  5: 성별=(1,)     나이=(1, 2)   가격=1 X
        상품  6: 성별=(1,)     나이=(1, 2)   가격=2 X
        상품  7: 성별=(2,)     나이=(1,)     가격=1 O
        상품  8: 성별=(2,)     나이=(1,)     가격=2 O
        상품  9: 성별=(2,)     나이=(2,)     가격=1 O
        상품 10: 성별=(2,)     나이=(2,)     가격=2 O
        상품 11: 성별=(2,)     나이=(1, 2)   가격=1 O
        상품 12: 성별=(2,)     나이=(1, 2)   가격=2 O
        상품 13: 성별=(1, 2)   나이=(1,)     가격=1 O
        상품 14: 성별=(1, 2)   나이=(1,)     가격=2 O
        상품 15: 성별=(1, 2)   나이=(2,)     가격=1 O
        상품 16: 성별=(1, 2)   나이=(2,)     가격=2 O
        상품 17: 성별=(1, 2)   나이=(1, 2)   가격=1 O
        상품 18: 성별=(1, 2)   나이=(1, 2)   가격=2 O
        '''
        GenderCategory.objects.filter(id=1).update(is_active=False)
        response = self.client.get(
            '/products',
            **self.auth
        )
        GenderCategory.objects.filter(id=1).update(is_active=True)

        self.assertEqual(response.status_code, 200)

        data = response.json()['data']
        self.assertEqual(len(data), 12)

        ids_list = list(map(lambda row: row['id'], data))
        self.assertEqual(ids_list, list(range(7, 19)))


class ProductDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()
        get_dummy_age()
        get_dummy_gender()
        get_dummy_price()
        get_dummy_product_category()
        get_dummy_product()

    def test_비인증(self):
        res = self.client.get('/products/1')
        self.assertEqual(res.status_code, 401)

    def test_찾을수없음(self):
        res = self.client.get('/products/2', **self.headers)
        self.assertEqual(res.status_code, 404)

    def test_정상조회(self):
        res = self.client.get('/products/1', **self.headers)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertTrue(data['success'])

        product = data['data']
        self.assertTrue(isinstance(product, dict))

        required_keys = [
            'id',
            'name',
            'description',
            'detail',
            'thumbnail',
            'image_url',
            'price',
        ]
        self.assertTrue(all(key in product for key in required_keys))
        self.assertTrue(isinstance(product['image_url'], list))


class AgeListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()

        cls.ages_count = 3
        for _ in range(cls.ages_count):
            get_dummy_age()

    def test_비인증(self):
        res = self.client.get('/ages')
        self.assertEqual(res.status_code, 401)

    def test_정상조회(self):
        res = self.client.get('/ages', **self.headers)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertTrue(data['success'])

        ages = data['data']
        self.assertTrue(isinstance(ages, list))
        self.assertEqual(len(ages), self.ages_count)

        age = ages[0]
        required_keys = ['id', 'value']
        self.assertTrue(all(key in age for key in required_keys))

    def test_비활성_필터링(self):
        AgeCategory.objects.filter(id=1).update(is_active=False)
        res = self.client.get('/ages', **self.headers)
        AgeCategory.objects.filter(id=1).update(is_active=True)
        self.assertEqual(res.status_code, 200)

        ages = res.json()['data']
        self.assertEqual(len(ages), self.ages_count - 1)


class GenderListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()

        cls.genders_count = 3
        for _ in range(cls.genders_count):
            get_dummy_gender()

    def test_비인증(self):
        res = self.client.get('/genders')
        self.assertEqual(res.status_code, 401)

    def test_정상조회(self):
        res = self.client.get('/genders', **self.headers)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertTrue(data['success'])

        genders = data['data']
        self.assertTrue(isinstance(genders, list))
        self.assertEqual(len(genders), self.genders_count)

        gender = genders[0]
        required_keys = ['id', 'name']
        self.assertTrue(all(key in gender for key in required_keys))

    def test_비활성_필터링(self):
        GenderCategory.objects.filter(id=1).update(is_active=False)
        res = self.client.get('/genders', **self.headers)
        GenderCategory.objects.filter(id=1).update(is_active=True)
        self.assertEqual(res.status_code, 200)

        genders = res.json()['data']
        self.assertEqual(len(genders), self.genders_count - 1)


class PriceListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.headers = jwt_to_headers(get_jwt(
            'test@test.co.kr',
            '1234'
        ))
        get_dummy_appmanager()

        cls.prices_count = 3
        for _ in range(cls.prices_count):
            get_dummy_price()

    def test_비인증(self):
        res = self.client.get('/prices')
        self.assertEqual(res.status_code, 401)

    def test_정상조회(self):
        res = self.client.get('/prices', **self.headers)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertTrue(data['success'])

        prices = data['data']
        self.assertTrue(isinstance(prices, list))
        self.assertEqual(len(prices), self.prices_count)

        price = prices[0]
        required_keys = ['id', 'value']
        self.assertTrue(all(key in price for key in required_keys))

    def test_비활성_필터링(self):
        PriceCategory.objects.filter(id=1).update(is_active=False)
        res = self.client.get('/prices', **self.headers)
        PriceCategory.objects.filter(id=1).update(is_active=True)
        self.assertEqual(res.status_code, 200)

        prices = res.json()['data']
        self.assertEqual(len(prices), self.prices_count - 1)


class ErrorHandlerTest(TestCase):
    def test_handler404(self):
        response = self.client.get('/not-found')
        self.assertEqual(response.status_code, 404)

        data = response.json()
        self.assertTrue('message' in data)
        self.assertTrue('success' in data)
        self.assertFalse(data['success'])

    def test_handler500(self):
        client = Client(raise_request_exception=False)
        response = client.get('/test_500')
        self.assertEqual(response.status_code, 500)

        data = response.json()
        self.assertTrue('message' in data)
        self.assertTrue('success' in data)
        self.assertFalse(data['success'])

import tempfile
import shutil

from django.core.files.images import ImageFile
from django.test import (
    TestCase,
    override_settings
)

from ..models import (
    AppManager,
    Product,
    AgeCategory,
    GenderCategory,
    PriceCategory,
    ProductCategory
)


MEDIA_ROOT = tempfile.mkdtemp()


def get_test_image_file():
    file = tempfile.NamedTemporaryFile(suffix='.png')
    return ImageFile(file, name='test.png')


def get_dummy_product(**kwargs):
    kwargs.setdefault('name', '상품명')
    kwargs.setdefault('category_id', 1)
    kwargs.setdefault('description', '상품소개')
    kwargs.setdefault('detail', '상품정보')
    kwargs.setdefault('vendor', '판매처')
    kwargs.setdefault('price_id', 1)
    kwargs.setdefault('link', 'https://link')
    kwargs.setdefault('consumer_price', '42')
    kwargs.setdefault('margin_rate', '42.42')
    kwargs.setdefault('thumbnail', get_test_image_file())

    gender_ids = kwargs.pop('gender_ids', [1])
    age_ids = kwargs.pop('age_ids', [1])

    product = Product.objects.create(**kwargs)

    product.gender.add(*gender_ids)
    product.age.add(*age_ids)

    return product


def get_dummy_age(**kwargs):
    kwargs.setdefault('name', '나이대')
    kwargs.setdefault('min', 0)
    kwargs.setdefault('max', 1)
    kwargs.setdefault('is_active', True)
    kwargs.setdefault('manager_id', 1)

    age = AgeCategory.objects.create(**kwargs)
    return age


def get_dummy_gender(**kwargs):
    kwargs.setdefault('name', '성별')
    kwargs.setdefault('is_active', True)
    kwargs.setdefault('manager_id', 1)

    gender = GenderCategory.objects.create(**kwargs)
    return gender


def get_dummy_price(**kwargs):
    kwargs.setdefault('value', 42)
    kwargs.setdefault('name', '가격대')
    kwargs.setdefault('is_active', True)
    kwargs.setdefault('manager_id', 1)

    price = PriceCategory.objects.create(**kwargs)
    return price


def get_dummy_product_category(**kwargs):
    kwargs.setdefault('name', '상품 카테고리')

    product_category = ProductCategory.objects.create(**kwargs)
    return product_category


def get_dummy_appmanager():
    return AppManager.objects.create()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestProductActivedFilter(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_dummy_appmanager()
        get_dummy_product_category()
        genders = [get_dummy_gender().id, get_dummy_gender().id]
        ages = [get_dummy_age().id, get_dummy_age().id]
        price = get_dummy_price().id

        get_dummy_product(
            gender_ids=genders,
            age_ids=ages,
            price_id=price,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.genders = GenderCategory.objects.all()
        self.ages = AgeCategory.objects.all()
        self.prices = PriceCategory.objects.all()
        self.product = Product.objects.first()

        '''
        모든 나이/성별/가격 is_active=True
        '''
        self.genders.update(is_active=True)
        self.ages.update(is_active=True)
        self.prices.update(is_active=True)

    def test_모두_활성(self):
        self.assertEqual(Product.objects.actived().count(), 1)

    def test_가격_비활성(self):
        self.prices.update(is_active=False)
        self.assertEqual(Product.objects.actived().count(), 0)

    def test_성별_일부_비활성(self):
        gender = self.genders.first()
        gender.is_active = False
        gender.save()

        '''
        상품에 활성화된 성별이 있으므로 상품은 활성화됨
        '''
        self.assertEqual(Product.objects.actived().count(), 1)

    def test_성별_모두_비활성(self):
        self.genders.update(is_active=False)

        '''
        상품에 활성화된 성별이 없으므로 상품은 비활성
        '''
        self.assertEqual(Product.objects.actived().count(), 0)

    def test_나이_일부_비활성(self):
        age = self.ages.first()
        age.is_active = False
        age.save()

        '''
        상품에 활성화된 나이가 있으므로 상품은 활성화됨
        '''
        self.assertEqual(Product.objects.actived().count(), 1)

    def test_나이_모두_비활성(self):
        self.ages.update(is_active=False)

        '''
        상품에 활성화된 나이가 없으므로 상품은 비활성
        '''
        self.assertEqual(Product.objects.actived().count(), 0)

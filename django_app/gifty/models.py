from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(
        '생성일',
        auto_now_add=True
    )
    updated = models.DateTimeField(
        '갱신일',
        auto_now=True
    )

    class Meta:
        abstract = True


class AppManager(BaseModel):
    class Meta:
        verbose_name = '앱관리'
        verbose_name_plural = '앱관리'

    def __str__(self):
        return '앱관리'


class GenderCategory(BaseModel):
    name = models.CharField(
        '이름',
        max_length=16
    )
    is_active = models.BooleanField(
        '활성화',
        default=True,
    )
    manager = models.ForeignKey(
        AppManager,
        on_delete=models.CASCADE,
        default=1,
        related_name='genders'
    )

    def __str__(self):
        return self.name


class AgeCategory(BaseModel):
    name = models.CharField(
        '이름',
        max_length=32,
        blank=True
    )
    min = models.PositiveIntegerField(
        '최솟값',
        null=True,
        blank=True
    )
    max = models.PositiveIntegerField(
        '최댓값',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        '활성화',
        default=True,
    )
    manager = models.ForeignKey(
        AppManager,
        on_delete=models.CASCADE,
        default=1,
        related_name='ages'
    )

    def __str__(self):
        return self.name or f'{self.min}~{self.max}'


class PriceCategory(BaseModel):
    value = models.PositiveIntegerField(
        '값'
    )
    name = models.CharField(
        '이름',
        max_length=32,
        blank=True
    )
    is_active = models.BooleanField(
        '활성화',
        default=True
    )
    manager = models.ForeignKey(
        AppManager,
        on_delete=models.CASCADE,
        default=1,
        related_name='prices'
    )

    def __str__(self):
        return str(self.value)


class ProductCategory(BaseModel):
    name = models.CharField(
        '이름',
        max_length=32
    )

    def __str__(self):
        return self.name


class Product(BaseModel):
    id = models.BigAutoField(
        '상품코드',
        primary_key=True
    )
    name = models.CharField(
        '상품명',
        max_length=128
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='상품유형',
        related_name='products',
        on_delete=models.CASCADE
    )
    thumbnail = models.ImageField(
        '썸네일',
        upload_to='product/thumbnail/%Y/%m/%d'
    )
    description = models.TextField(
        '상품설명',
        blank=True
    )
    detail = models.TextField(
        '상품정보',
        blank=True
    )
    vendor = models.CharField(
        '판매처',
        max_length=64,
    )
    views = models.PositiveIntegerField(
        '노출수',
        default=0
    )
    likes = models.ManyToManyField(
        'order.Receiver',
        related_name='likes'
    )
    dislikes = models.ManyToManyField(
        'order.Receiver',
        related_name='dislikes',
    )
    gender = models.ManyToManyField(
        GenderCategory,
        related_name='products'
    )
    age = models.ManyToManyField(
        AgeCategory,
        related_name='products'
    )
    price = models.ForeignKey(
        PriceCategory,
        related_name='products',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = '상품'
        verbose_name_plural = '상품관리'


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        '상품 상세 이미지',
        upload_to='product/images/%Y/%m/%d'
    )

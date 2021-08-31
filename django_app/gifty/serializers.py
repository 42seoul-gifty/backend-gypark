from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField
)

from django.db.models import (
    Max,
    Min
)

from .models import Product


class ProductSerializer(ModelSerializer):
    price = SerializerMethodField()
    image_url = SerializerMethodField()
    # age_min = SerializerMethodField()
    # age_max = SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'detail',
            'price',
            'thumbnail',
            'image_url',
            # 'age_min',
            # 'age_max',
        )

    def get_age_min(self, obj):
        return obj.age.aggregate(Min('min'))['min__min']

    def get_age_max(self, obj):
        return obj.age.aggregate(Max('max'))['max__max']

    def get_price(self, obj):
        return obj.price.value

    def get_image_url(self, obj):
        urls = obj.images.values_list('image', flat=True)
        request = self.context.get('request', None)

        return map(
            lambda url: request.build_absolute_uri(url),
            urls
        )